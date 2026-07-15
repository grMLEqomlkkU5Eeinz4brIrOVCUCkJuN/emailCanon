# emailCanon

A Python library for email address canonicalization and normalization. Normalizes email addresses according to provider-specific rules (Gmail, Outlook, Yahoo, etc.) to help identify duplicate accounts and standardize email formats.

This is the Python equivalent of [@grml/nomadic](https://github.com/grMLEqomlkkU5Eeinz4brIrOVCUCkJuN/nomad).

## Features

- **Provider-aware normalization**: Applies provider-specific rules (sub-address stripping, dot removal, case-folding)
- **Canonical domain collapsing**: Maps alias domains to canonical domains (e.g., `googlemail.com` becomes `gmail.com`)
- **Sub-address stripping**: Removes subaddresses (e.g., `user+tag` becomes `user`) per provider
- **RFC-compliant**: Handles quoted local parts and validates email structure
- **Customizable**: Extend with custom providers or override default rules
- **Built-in providers**: Gmail, Microsoft (Outlook/Hotmail), Yahoo, Apple iCloud, Fastmail, ProtonMail, and 10+ others

## Installation

```bash
pip install emailcanon
```

## Quick Start

```python
from emailcanon import normalizeEmail, getEmailProvider, isSameEmail

# Basic normalization
normalized = normalizeEmail("Test.User+Tag@Gmail.com")
print(normalized)  # "testuser@gmail.com"

# Get the provider ID
provider = getEmailProvider("user@outlook.com")
print(provider)  # "microsoft"

# Check if two emails are equivalent
same = isSameEmail("john.doe+newsletter@gmail.com", "johndoe@googlemail.com")
print(same)  # True
```

## API Reference

### `normalizeEmail(email: str, options: NormalizeOptions | None = None) -> str`

Normalizes an email address to its canonical form.

Applies provider-specific rules including:
- Sub-address stripping (e.g., `+tag` for Gmail)
- Dot removal (Gmail ignores dots in the local part)
- Case folding of the local part
- Canonical domain mapping (alias domains to primary domain)

**Parameters:**
- `email`: The email address to normalize
- `options`: Optional normalization options (see `NormalizeOptions` below)

**Returns:** Canonical email string. The string is returned regardless of
whether the address is structurally valid; this function discards the `valid`
flag. If you need the validity flag or the parsed components, use
[`normalizeEmailDetailed`](#normalizeemaildetailedemail-str-options-normalizeoptions--none--none---normalizedemail).

**Raises:** `TypeError` if email is not a string

**Examples:**
```python
normalizeEmail("john.doe+newsletter@GMAIL.COM")  # "johndoe@gmail.com"
normalizeEmail("first.name@outlook.com")         # "firstname@outlook.com"
normalizeEmail("user-tag@yahoo.com")             # "user@yahoo.com"
normalizeEmail("\"quoted.local\"@example.com")   # "\"quoted.local\"@example.com"
```

### `normalizeEmailDetailed(email: str, options: NormalizeOptions | None = None) -> NormalizedEmail`

Normalizes an email and returns detailed information about the normalization.

**Returns:** `NormalizedEmail` object with:
- `normalized`: Canonical email string
- `local`: Normalized local part
- `domain`: Normalized domain
- `providerId`: ID of matched provider (e.g., "gmail"), or `None`
- `subaddress`: Extracted sub-address (e.g., "tag" from "user+tag"), or `None`
  (an empty tag such as `user+` yields `None`, just like having no separator)
- `valid`: Whether the email is structurally valid (see
  [Validity flag limitations](#validity-flag-limitations))

**Example:**
```python
result = normalizeEmailDetailed("john+newsletter@gmail.com")
# NormalizedEmail(
#     normalized="john@gmail.com",
#     local="john",
#     domain="gmail.com",
#     providerId="gmail",
#     subaddress="newsletter",
#     valid=True
# )
```

### `getEmailProvider(email: str, options: NormalizeOptions | None = None) -> str | None`

Returns the provider ID for an email address, or `None` if no provider matches.

**Parameters:**
- `email`: The email address
- `options`: Optional normalization options

**Returns:** Provider ID string (e.g., "gmail", "microsoft") or `None`

**Raises:** `TypeError` if email is not a string

**Example:**
```python
getEmailProvider("user@gmail.com")           # "gmail"
getEmailProvider("name@outlook.com")        # "microsoft"
getEmailProvider("person@example.com")      # None
```

### `isSameEmail(a: str, b: str, options: NormalizeOptions | None = None) -> bool`

Checks if two email addresses normalize to the same canonical form.

Useful for detecting duplicate accounts where users registered with different aliases.

**Parameters:**
- `a`, `b`: Email addresses to compare
- `options`: Optional normalization options

**Returns:** `True` if both emails normalize identically, `False` otherwise

**Example:**
```python
isSameEmail("john.doe@gmail.com", "johndoe+spam@googlemail.com")  # True
isSameEmail("john@example.com", "jane@example.com")               # False
```

## Configuration

### `NormalizeOptions`

Control normalization behavior via options:

```python
from emailcanon import NormalizeOptions, ProviderRule, normalizeEmail

options = NormalizeOptions(
    lowercaseDomain=True,              # Default: True
    providers=[                        # Custom providers to add/override
        ProviderRule(
            id="custom",
            domains=["custom.example.com"],
            lowercaseLocal=True,
            removeDots=True,
            subaddressSeparators=["+"]
        )
    ],
    replaceDefaultProviders=False,     # Keep built-in providers
    defaultRule=None                   # Rule for unknown domains
)

normalized = normalizeEmail("user@custom.example.com", options)
```

**Caching note:** The provider registry built from a `NormalizeOptions`
instance is memoized per options object (keyed on identity), so reusing the
same `options` across many calls avoids rebuilding the registry every time.
Because the cache is keyed on object identity, mutating an `options` object
after its first use will not be reflected. This is where you construct a fresh `NormalizeOptions` instead of mutating one.

### `ProviderRule`

Define custom email provider rules:

```python
ProviderRule(
    id="my_provider",                           # Unique identifier
    domains=["example.com", "mail.example.com"],  # Domain patterns
    lowercaseLocal=True,                        # Convert local part to lowercase
    removeDots=True,                            # Remove dots from local part
    subaddressSeparators=["+", "-"],            # Characters that separate subaddress
    canonicalDomain="example.com"               # Map all domains to this
)
```

## Supported Providers

| Provider | ID | Domains | Rules |
|----------|----|---------| ----- |
| **Gmail** | `gmail` | gmail.com, googlemail.com | Lowercase, remove dots, `+` subaddress, maps to gmail.com |
| **Microsoft** | `microsoft` | outlook.com*, hotmail.com*, live.com*, msn.com, others | Lowercase, `+` subaddress |
| **Yahoo** | `yahoo` | yahoo.com*, ymail.com, rocketmail.com | Lowercase, `-` subaddress |
| **Apple iCloud** | `icloud` | icloud.com, me.com, mac.com | Lowercase, `+` subaddress |
| **Fastmail** | `fastmail` | fastmail.com, fastmail.fm | Lowercase, `+` subaddress |
| **ProtonMail** | `proton` | protonmail.com, protonmail.ch, proton.me, pm.me | Lowercase, `+` subaddress |
| **Yandex** | `yandex` | yandex.com, yandex.ru, ya.ru, others | Lowercase, `+` subaddress |
| **Zoho** | `zoho` | zoho.com, zohomail.com, zoho.eu | Lowercase, `+` subaddress |
| **Tutanota** | `tutanota` | tutanota.com, tutanota.de, tutamail.com, tuta.com, others | Lowercase, `+` subaddress |
| **Posteo** | `posteo` | posteo.de, posteo.net | Lowercase, `+` subaddress |
| **Mailbox.org** | `mailbox` | mailbox.org | Lowercase, `+` subaddress |
| **Mailfence** | `mailfence` | mailfence.com | Lowercase, `+` subaddress |
| **Runbox** | `runbox` | runbox.com | Lowercase, `+` subaddress |
| **Pobox** | `pobox` | pobox.com | Lowercase, `+` subaddress |
| **AOL** | `aol` | aol.com, aim.com | Lowercase |

*\* Multiple regional variants supported (com.au, co.uk, de, fr, etc.)*

## Examples

### Duplicate Account Detection

```python
from emailcanon import normalizeEmail

emails = [
    "john.doe@gmail.com",
    "johndoe+shopping@googlemail.com",
    "john.doe@yahoo.com",
    "J.DOE@GMAIL.COM"
]

# Group by normalized form
normalized_map = {}
for email in emails:
    norm = normalizeEmail(email)
    if norm not in normalized_map:
        normalized_map[norm] = []
    normalized_map[norm].append(email)

# Find duplicates
for norm_email, originals in normalized_map.items():
    if len(originals) > 1:
        print(f"Duplicates: {originals} maps to {norm_email}")
        # Output: Duplicates: ['john.doe@gmail.com', 'johndoe+shopping@googlemail.com', 'J.DOE@GMAIL.COM'] maps to john@gmail.com
```

### Custom Provider Rules

```python
from emailcanon import normalizeEmail, NormalizeOptions, ProviderRule

# Add custom provider
options = NormalizeOptions(
    providers=[
        ProviderRule(
            id="company",
            domains=["company.com", "corp.company.com"],
            canonicalDomain="company.com",
            lowercaseLocal=True,
            subaddressSeparators=["+"]
        )
    ]
)

normalizeEmail("User+Team@corp.company.com", options)
# "user@company.com"
```

### Skip Default Providers

```python
from emailcanon import normalizeEmail, NormalizeOptions, ProviderRule

# Use only custom providers, ignore built-in ones
options = NormalizeOptions(
    replaceDefaultProviders=True,
    providers=[
        ProviderRule(
            id="custom",
            domains=["custom.local"],
            lowercaseLocal=True
        )
    ]
)

normalizeEmail("User@custom.local", options)
# "user@custom.local"
```

## Design Notes

- **Conservative by default**: Unknown domains get minimal normalization (lowercase domain only, local part unchanged)
- **Quoted strings**: RFC 5321 quoted local parts (e.g., `"user name"@example.com`) are preserved verbatim
- **Domain validation**: Domains must follow standard DNS naming (labels separated by dots, alphanumeric + hyphens)
- **Immutable rules**: Provider rules are frozen dataclasses; mutation is not possible

### Validity flag limitations

The `valid` flag returned by `normalizeEmailDetailed` is a pragmatic structural
check, not a full RFC 5321/5322 validator. In particular, the domain check has
two known limitations:

- **Single-label hosts are rejected.** The domain must contain at least one dot,
  so hosts like `localhost` are reported as `valid=False`, even though they are
  deliverable in some environments.
- **Non-ASCII / IDN domains are rejected.** The check is ASCII-only, so
  internationalized domains such as `münchen.de` are reported as
  `valid=False`. Pre-encode them to Punycode (`xn--mnchen-3ya.de`) if you need
  them to pass.

These limitations only affect the `valid` flag; normalization of the local part
and domain is still performed in all cases.

## Why Email Canonicalization?

Email addresses can look different but deliver to the same mailbox:

| Input | Gmail Reality |
|-------|---------------|
| `john.doe@gmail.com` | `johndoe@gmail.com` (dots ignored) |
| `johndoe+newsletter@gmail.com` | `johndoe@gmail.com` (subaddress stripped) |
| `johndoe@googlemail.com` | `johndoe@gmail.com` (domain alias) |

Without canonicalization, a user could register multiple accounts. emailCanon standardizes these to detect and prevent duplicate registrations.

## Development

Set up a local virtual environment and install the package with its dev
dependencies (mypy, ruff):

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install the package in editable mode with dev extras
pip install -e ".[dev]"
```

Then run the tooling:

```bash
# Run the test suite (the test files are named after the area they cover,
# e.g. gmail.py, so discovery needs an explicit pattern)
python -m unittest discover -s tests -p "*.py"

# ...or run a single test module directly
python -m unittest tests.gmail

mypy            # type-check
ruff format     # format with tabs
ruff check      # lint
```

When you're done, leave the environment with `deactivate`.

## References

Provider rules compiled from:
- Wikipedia, [Email address](https://en.wikipedia.org/wiki/Email_address) (sub-addressing section)
- [aaronbassett's Email sub-addressing gist](https://gist.github.com/aaronbassett/4135599)
- [validator.js](https://github.com/validatorjs/validator.js) normalizeEmail conventions
- Official provider documentation (Fastmail, Microsoft Learn, Proton)

## License

MIT
