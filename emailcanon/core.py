import re
from collections.abc import Sequence
from functools import lru_cache
from weakref import WeakKeyDictionary

from ._types import (
	DefaultRule,
	EmailParts,
	LocalPartRule,
	LocalPartRules,
	NormalizedEmail,
	NormalizeOptions,
	ProviderRule,
)
from .providers import DEFAULT_PROVIDERS

CONSERVATIVE_DEFAULT: DefaultRule = LocalPartRules(
	lowercaseLocal=False, removeDots=False, subaddressSeparators=[]
)

# Known limitations of the structural validity check encoded by DOMAIN_RE:
#   - It requires at least one dot, so single-label hosts such as "localhost"
#     are reported as invalid (valid=False), even though they are deliverable
#     in some environments.
#   - It is ASCII-only, so internationalized (IDN) / Unicode domains such as
#     "münchen.de" are reported as invalid. Punycode-encoded forms
#     ("xn--mnchen-3ya.de") are accepted.
# These only affect the `valid` flag; normalization itself is still performed.
DOMAIN_RE = re.compile(
	r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+$",
	re.IGNORECASE,
)

# Memoization of registries built from custom-provider options. Keyed weakly on
# the NormalizeOptions instance, because the realistic bulk-dedup pattern reuses
# the same options object across many emails (e.g. isSameEmail, or a loop). The
# weak keying lets entries be collected once the options object is gone.
#
# Caveat: the cache is keyed on object identity, so mutating an options object
# after its first use will NOT be reflected in subsequent calls. Build a fresh
# NormalizeOptions instead of mutating one in place.
_customRegistryCache: "WeakKeyDictionary[NormalizeOptions, dict[str, ProviderRule]]" = (
	WeakKeyDictionary()
)


def buildRegistry(providers: Sequence[ProviderRule]) -> dict[str, ProviderRule]:
	provider_map: dict[str, ProviderRule] = {}
	for provider in providers:
		for domain in provider.domains:
			provider_map[domain.lower()] = provider

	return provider_map


@lru_cache(maxsize=1)
def _defaultRegistry() -> dict[str, ProviderRule]:
	"""Build (and cache) the registry for the default-providers path.

	Cached for the lifetime of the process; the default providers are immutable
	frozen dataclasses, so a single shared registry is safe to reuse.
	"""
	return buildRegistry(DEFAULT_PROVIDERS)


def getRegistry(options: NormalizeOptions) -> dict[str, ProviderRule]:
	"""Resolve the domain->ProviderRule registry for the given options.

	The default-providers path is cached process-wide. When custom providers
	are supplied (or defaults are replaced), the resulting registry is memoized
	per options instance, so reusing the same options object across many calls
	avoids rebuilding the full registry every time. Mutating an options object
	after its first use will not be reflected (see ``_customRegistryCache``).
	"""
	if not options.providers and not options.replaceDefaultProviders:
		return _defaultRegistry()

	cached = _customRegistryCache.get(options)
	if cached is not None:
		return cached

	base = [] if options.replaceDefaultProviders else DEFAULT_PROVIDERS
	providers_list = options.providers if options.providers is not None else []
	registry = buildRegistry([*base, *providers_list])
	_customRegistryCache[options] = registry
	return registry


def splitEmail(email: str) -> EmailParts | None:
	at = email.rfind("@")
	if at <= 0 or at == len(email) - 1:
		return None

	return EmailParts(local=email[0:at], domain=email[at + 1 :])


def isQuoted(local: str) -> bool:
	return len(local) >= 2 and local.startswith('"') and local.endswith('"')


def stripSubaddress(local: str, separators: list[str]) -> tuple[str, str | None]:
	cut = -1
	cut_len = 0
	for sep in separators:
		if not sep:
			continue
		idx = local.find(sep)
		if idx > 0 and (cut == -1 or idx < cut):
			cut = idx
			cut_len = len(sep)

	if cut == -1:
		return (local, None)

	subaddress = local[cut + cut_len :]
	# An empty tag (e.g. "user+@gmail.com") carries no sub-address information,
	# so normalize it to None to keep the "no subaddress" contract consistent
	# with the no-separator case above.
	return (local[:cut], subaddress if subaddress else None)


def isValidLocal(local: str) -> bool:
	if len(local) == 0:
		return False
	if isQuoted(local):
		return True
	return not re.search(r"[\s@]", local)


def _prepare(
	email: object, options: NormalizeOptions | None
) -> tuple[str, NormalizeOptions]:
	"""Apply the shared input guard used by the public entry points.

	Defaults ``options`` and rejects non-string ``email`` with a TypeError.
	Returns the validated email string and resolved options.
	"""
	if options is None:
		options = NormalizeOptions()
	if not isinstance(email, str):
		raise TypeError(
			f"Expected email to be a string, received {type(email).__name__}"
		)
	return email, options


def normalizeEmailDetailed(
	email: str, options: NormalizeOptions | None = None
) -> NormalizedEmail:
	email, options = _prepare(email, options)

	lowercase_domain = (
		options.lowercaseDomain if options.lowercaseDomain is not None else True
	)
	trimmed = email.strip()
	parts = splitEmail(trimmed)

	if not parts:
		return NormalizedEmail(
			normalized=trimmed,
			local=trimmed,
			domain="",
			providerId=None,
			subaddress=None,
			valid=False,
		)

	lookup_domain = parts.domain.lower()
	registry = getRegistry(options)
	provider = registry.get(lookup_domain)
	rule: LocalPartRule = (
		provider
		if provider
		else (options.defaultRule if options.defaultRule else CONSERVATIVE_DEFAULT)
	)

	local = parts.local
	subaddress: str | None = None

	if not isQuoted(local):
		local, subaddress = stripSubaddress(
			local, rule.subaddressSeparators if rule.subaddressSeparators else []
		)
		if rule.removeDots:
			local = local.replace(".", "")
		if rule.lowercaseLocal:
			local = local.lower()

	domain = lookup_domain if lowercase_domain else parts.domain
	if provider and provider.canonicalDomain:
		domain = (
			provider.canonicalDomain.lower()
			if lowercase_domain
			else provider.canonicalDomain
		)

	valid = isValidLocal(local) and DOMAIN_RE.match(domain) is not None

	return NormalizedEmail(
		normalized=f"{local}@{domain}",
		local=local,
		domain=domain,
		providerId=provider.id if provider else None,
		subaddress=subaddress,
		valid=valid,
	)


def normalizeEmail(email: str, options: NormalizeOptions | None = None) -> str:
	"""Normalize an email and return only the canonical string.

	The normalized string is returned regardless of whether the address is
	structurally valid; this function discards the ``valid`` flag and the rest
	of the structured result. Callers that need the validity flag or the parsed
	components (local, domain, providerId, subaddress) should use
	``normalizeEmailDetailed`` instead.
	"""
	return normalizeEmailDetailed(email, options).normalized


def getEmailProvider(email: str, options: NormalizeOptions | None = None) -> str | None:
	email, options = _prepare(email, options)
	parts = splitEmail(email.strip())
	if not parts:
		return None
	provider = getRegistry(options).get(parts.domain.lower())
	return provider.id if provider else None


def isSameEmail(a: str, b: str, options: NormalizeOptions | None = None) -> bool:
	return normalizeEmail(a, options) == normalizeEmail(b, options)
