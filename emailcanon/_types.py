from dataclasses import dataclass
from typing import Protocol


class LocalPartRule(Protocol):
	"""Structural contract for the local-part normalization rules.

	Both ``ProviderRule`` and ``LocalPartRules`` satisfy this protocol; the
	normalization core only needs these three attributes to canonicalize a
	local part, so it depends on this protocol rather than a concrete type.
	"""

	@property
	def lowercaseLocal(self) -> bool | None: ...

	@property
	def removeDots(self) -> bool | None: ...

	@property
	def subaddressSeparators(self) -> list[str] | None: ...


@dataclass(frozen=True)
class LocalPartRules:
	lowercaseLocal: bool | None = None
	removeDots: bool | None = None
	subaddressSeparators: list[str] | None = None


@dataclass(frozen=True)
class ProviderRule:
	id: str
	domains: list[str]
	lowercaseLocal: bool | None = None
	removeDots: bool | None = None
	subaddressSeparators: list[str] | None = None
	canonicalDomain: str | None = None


type DefaultRule = LocalPartRules


# eq=False keeps the default identity-based __hash__/__eq__, which makes
# NormalizeOptions usable as a key in the identity-keyed WeakKeyDictionary
# registry cache (a value-based __eq__ would null out __hash__). Two distinct
# options objects are intentionally never "equal".
@dataclass(eq=False)
class NormalizeOptions:
	providers: list[ProviderRule] | None = None
	replaceDefaultProviders: bool | None = None
	defaultRule: DefaultRule | None = None
	lowercaseDomain: bool | None = None


@dataclass
class NormalizedEmail:
	normalized: str
	local: str
	domain: str
	valid: bool
	providerId: str | None = None
	subaddress: str | None = None


@dataclass
class EmailParts:
	local: str
	domain: str
