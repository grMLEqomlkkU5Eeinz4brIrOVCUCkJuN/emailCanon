import re
from providers import DEFAULT_PROVIDERS
from _types import DefaultRule, NormalizeOptions, NormalizedEmail, ProviderRule, LocalPartRules

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
