import re
from providers import DEFAULT_PROVIDERS
from _types import DefaultRule, NormalizeOptions, EmailParts, NormalizedEmail, ProviderRule, LocalPartRules

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
		local = email[0:at],
		domain = email[at + 1]
	)


def isQuoted(local: str) -> bool:
	return len(local) >=2 and local.startswith('"') and local.startswith("'")