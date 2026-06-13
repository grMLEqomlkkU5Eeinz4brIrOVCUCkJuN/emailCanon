from dataclasses import dataclass

@dataclass(frozen=True)
class LocalPartRules:
	lowercaseLocal: bool | None = None
	removeDots: bool | None = None
	subaddressSeparators: list[str] | None = None

@dataclass
class ProviderRule:
	id: str
	domains: list[str]
	lowercaseLocal: bool | None = None
	removeDots: bool | None = None
	subaddressSeparators: list[str] | None = None
	canonicalDomain: list[str] | None = None

type DefaultRule = LocalPartRules

@dataclass
class NormalizeOptions:
	providers: list[ProviderRule]| None = None
	replaceDefaultProviders: bool | None = None
	defaultRule: DefaultRule| None = None
	lowercaseDomain: bool| None = None

@dataclass
class NormalizedEmail:
	normalized: str
	local: str
	domain: str
	valid: bool
	providerId: str | None = None
	subaddress: str | None = None