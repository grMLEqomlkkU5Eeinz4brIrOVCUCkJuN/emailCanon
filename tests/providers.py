import unittest

from emailcanon import (
	DEFAULT_PROVIDERS,
	getEmailProvider,
	isSameEmail,
	normalizeEmail,
)


class TestMicrosoft(unittest.TestCase):
	def test_strips_tag_but_keeps_dots(self):
		self.assertEqual(
			normalizeEmail("John.Doe+news@outlook.com"), "john.doe@outlook.com"
		)

	def test_does_not_collapse_distinct_domains(self):
		self.assertEqual(normalizeEmail("user@hotmail.com"), "user@hotmail.com")
		self.assertFalse(isSameEmail("user@hotmail.com", "user@outlook.com"))

	def test_dots_are_significant(self):
		self.assertFalse(isSameEmail("a.b@outlook.com", "ab@outlook.com"))


class TestYahoo(unittest.TestCase):
	def test_uses_dash_as_subaddress_separator(self):
		self.assertEqual(normalizeEmail("john-shopping@yahoo.com"), "john@yahoo.com")

	def test_does_not_treat_plus_as_separator(self):
		self.assertEqual(normalizeEmail("john+tag@yahoo.com"), "john+tag@yahoo.com")

	def test_keeps_dots(self):
		self.assertEqual(normalizeEmail("john.doe@ymail.com"), "john.doe@ymail.com")


class TestPlusTagProviders(unittest.TestCase):
	def test_plus_tag_is_stripped(self):
		cases = [
			("Jane+lists@icloud.com", "jane@icloud.com"),
			("Jane+lists@proton.me", "jane@proton.me"),
			("Jane+lists@fastmail.com", "jane@fastmail.com"),
			("Jane+lists@yandex.ru", "jane@yandex.ru"),
			("Jane+lists@zoho.com", "jane@zoho.com"),
			("Jane+lists@mailfence.com", "jane@mailfence.com"),
			("Jane+lists@runbox.com", "jane@runbox.com"),
			("Jane+lists@pobox.com", "jane@pobox.com"),
			("Jane+lists@tuta.com", "jane@tuta.com"),
			("Jane+lists@posteo.de", "jane@posteo.de"),
			("Jane+lists@mailbox.org", "jane@mailbox.org"),
		]
		for input_email, expected in cases:
			with self.subTest(input=input_email):
				self.assertEqual(normalizeEmail(input_email), expected)

	def test_aol_lowercases_but_keeps_tag(self):
		self.assertEqual(normalizeEmail("Jane+lists@aol.com"), "jane+lists@aol.com")


class TestProviderDetection(unittest.TestCase):
	def test_gmail_is_detected(self):
		self.assertEqual(getEmailProvider("a@gmail.com"), "gmail")

	def test_microsoft_is_detected_across_tlds(self):
		self.assertEqual(getEmailProvider("a@hotmail.co.uk"), "microsoft")

	def test_yahoo_is_detected(self):
		self.assertEqual(getEmailProvider("a@yahoo.fr"), "yahoo")

	def test_matching_is_case_insensitive(self):
		self.assertEqual(getEmailProvider("a@GmAiL.cOm"), "gmail")

	def test_unknown_domain_returns_none(self):
		self.assertIsNone(getEmailProvider("a@example.com"))

	def test_invalid_input_returns_none(self):
		self.assertIsNone(getEmailProvider("nope"))


class TestDefaultProviders(unittest.TestCase):
	def test_core_providers_are_exported(self):
		ids = [p.id for p in DEFAULT_PROVIDERS]
		self.assertIn("gmail", ids)
		self.assertIn("microsoft", ids)
		self.assertIn("yahoo", ids)

	def test_no_domain_is_duplicated(self):
		seen = set()
		for provider in DEFAULT_PROVIDERS:
			for domain in provider.domains:
				self.assertNotIn(domain, seen, f"duplicate domain {domain}")
				seen.add(domain)


if __name__ == "__main__":
	unittest.main()
