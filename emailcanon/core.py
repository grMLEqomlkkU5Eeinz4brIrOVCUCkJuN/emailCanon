import re
from .providers import DEFAULT_PROVIDERS
from ._types import DefaultRule, NormalizeOptions, EmailParts, NormalizedEmail, ProviderRule, LocalPartRules

CONSERVATIVE_DEFAULT: DefaultRule = LocalPartRules(
	lowercaseLocal = False,
	removeDots = False,
	subaddressSeparators = []
)

DOMAIN_RE = re.compile(
	r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+$",
	re.IGNORECASE
)

defaultRegistry: dict[str, ProviderRule] | None = None

def buildRegistry(providers: list[ProviderRule]) -> dict[str, ProviderRule]:
	providerMap:  dict[str, ProviderRule] = {}
	for provider in providers:
		for domain in provider.domains:
			providerMap[domain.lower()] = provider

	return providerMap

def getRegistry(options: NormalizeOptions) -> dict[str, ProviderRule]:
	global defaultRegistry

	if not options.providers and not options.replaceDefaultProviders:
		if defaultRegistry is None:
			defaultRegistry = buildRegistry(DEFAULT_PROVIDERS)
		return defaultRegistry

	base = [] if options.replaceDefaultProviders else DEFAULT_PROVIDERS

	providers_list = options.providers if options.providers is not None else []
	return buildRegistry([*base, *providers_list])

def splitEmail(email: str) -> EmailParts | None:
	at = email.rfind("@")
	if at <= 0 or at == len(email) - 1:
		return None

	return EmailParts(
		local=email[0:at],
		domain=email[at + 1:]
	)

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
	return (local[:cut], local[cut + cut_len:])

def isValidLocal(local: str) -> bool:
	if len(local) == 0:
		return False
	if isQuoted(local):
		return True
	return not re.search(r'[\s@]', local)

def normalizeEmailDetailed(email: str, options: NormalizeOptions | None = None) -> NormalizedEmail:
	if options is None:
		options = NormalizeOptions()

	if not isinstance(email, str):
		raise TypeError(f"Expected email to be a string, received {type(email).__name__}")

	lowercase_domain = options.lowercaseDomain if options.lowercaseDomain is not None else True
	trimmed = email.strip()
	parts = splitEmail(trimmed)

	if not parts:
		return NormalizedEmail(
			normalized=trimmed,
			local=trimmed,
			domain="",
			providerId=None,
			subaddress=None,
			valid=False
		)

	lookup_domain = parts.domain.lower()
	registry = getRegistry(options)
	provider = registry.get(lookup_domain)
	rule = provider if provider else (options.defaultRule if options.defaultRule else CONSERVATIVE_DEFAULT)

	local = parts.local
	subaddress: str | None = None

	if not isQuoted(local):
		local, subaddress = stripSubaddress(local, rule.subaddressSeparators if rule.subaddressSeparators else [])
		if rule.removeDots:
			local = local.replace(".", "")
		if rule.lowercaseLocal:
			local = local.lower()

	domain = lookup_domain if lowercase_domain else parts.domain
	if provider and provider.canonicalDomain:
		domain = provider.canonicalDomain.lower() if lowercase_domain else provider.canonicalDomain

	valid = isValidLocal(local) and DOMAIN_RE.match(domain) is not None

	return NormalizedEmail(
		normalized=f"{local}@{domain}",
		local=local,
		domain=domain,
		providerId=provider.id if provider else None,
		subaddress=subaddress,
		valid=valid
	)

def normalizeEmail(email: str, options: NormalizeOptions | None = None) -> str:
	return normalizeEmailDetailed(email, options).normalized

def getEmailProvider(email: str, options: NormalizeOptions | None = None) -> str | None:
	if options is None:
		options = NormalizeOptions()
	if not isinstance(email, str):
		raise TypeError(f"Expected email to be a string, received {type(email).__name__}")
	parts = splitEmail(email.strip())
	if not parts:
		return None
	provider = getRegistry(options).get(parts.domain.lower())
	return provider.id if provider else None

def isSameEmail(a: str, b: str, options: NormalizeOptions | None = None) -> bool:
	return normalizeEmail(a, options) == normalizeEmail(b, options)