from collections.abc import Sequence
from typing import Final

from ._types import ProviderRule

"""
Built-in provider rules.

These encode the well-documented, widely-relied-upon behaviors of major mail
providers. They are deliberately conservative: domains are only collapsed
where aliases truly deliver to the same mailbox (Gmail), and local parts are
only lowercased for providers known to be case-insensitive.

Sources cross-checked while compiling this list:
   - Wikipedia, "Email address" (sub-addressing section).
   - aaronbassett's "Email sub addressing for different providers" gist.
   - validator.js `normalizeEmail` provider conventions.
   - Fastmail / Microsoft Learn / Proton provider documentation.

Consumers can extend or override any of these via
{@link NormalizeOptions.providers}.
"""
DEFAULT_PROVIDERS: Final[Sequence[ProviderRule]] = (
	ProviderRule(
		id="gmail",
		domains=["gmail.com", "googlemail.com"],
		canonicalDomain="gmail.com",
		lowercaseLocal=True,
		removeDots=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="microsoft",
		domains=[
			"outlook.com",
			"outlook.com.au",
			"outlook.co.uk",
			"outlook.fr",
			"outlook.de",
			"outlook.es",
			"outlook.it",
			"outlook.jp",
			"hotmail.com",
			"hotmail.co.uk",
			"hotmail.com.au",
			"hotmail.fr",
			"hotmail.de",
			"hotmail.it",
			"hotmail.es",
			"hotmail.ca",
			"live.com",
			"live.com.au",
			"live.co.uk",
			"live.fr",
			"live.de",
			"live.ca",
			"msn.com",
			"windowslive.com",
			"passport.com",
		],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="yahoo",
		domains=[
			"yahoo.com",
			"yahoo.co.uk",
			"yahoo.ie",
			"yahoo.fr",
			"yahoo.de",
			"yahoo.es",
			"yahoo.it",
			"yahoo.ca",
			"yahoo.in",
			"yahoo.com.au",
			"yahoo.com.br",
			"yahoo.com.mx",
			"yahoo.com.ar",
			"yahoo.co.jp",
			"ymail.com",
			"rocketmail.com",
		],
		lowercaseLocal=True,
		subaddressSeparators=["-"],
	),
	ProviderRule(
		id="icloud",
		domains=["icloud.com", "me.com", "mac.com"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="fastmail",
		domains=["fastmail.com", "fastmail.fm"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="proton",
		domains=["protonmail.com", "protonmail.ch", "proton.me", "pm.me"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="yandex",
		domains=[
			"yandex.com",
			"yandex.ru",
			"ya.ru",
			"yandex.by",
			"yandex.kz",
			"yandex.ua",
		],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="zoho",
		domains=["zoho.com", "zohomail.com", "zoho.eu"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="mailfence",
		domains=["mailfence.com"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="runbox",
		domains=["runbox.com"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="pobox",
		domains=["pobox.com"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="tutanota",
		domains=[
			"tutanota.com",
			"tutanota.de",
			"tutamail.com",
			"tuta.com",
			"tuta.io",
			"keemail.me",
		],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="posteo",
		domains=["posteo.de", "posteo.net"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="mailbox",
		domains=["mailbox.org"],
		lowercaseLocal=True,
		subaddressSeparators=["+"],
	),
	ProviderRule(
		id="aol",
		domains=["aol.com", "aim.com"],
		lowercaseLocal=True,
	),
)
