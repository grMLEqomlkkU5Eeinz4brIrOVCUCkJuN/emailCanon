import unittest

from emailcanon import (
	LocalPartRules,
	NormalizeOptions,
	ProviderRule,
	getEmailProvider,
	isSameEmail,
	normalizeEmail,
)


class TestCustomProvider(unittest.TestCase):
	def setUp(self):
		corporate = ProviderRule(
			id="corp",
			domains=["mycompany.com", "mycompany.co"],
			canonicalDomain="mycompany.com",
			lowercaseLocal=True,
			removeDots=True,
			subaddressSeparators=["+"],
		)
		self.options = NormalizeOptions(providers=[corporate])

	def test_user_defined_provider_is_applied(self):
		self.assertEqual(
			normalizeEmail("John.Doe+x@mycompany.com", self.options),
			"johndoe@mycompany.com",
		)

	def test_custom_alias_domain_is_collapsed(self):
		self.assertEqual(
			normalizeEmail("john@mycompany.co", self.options), "john@mycompany.com"
		)

	def test_builtins_still_apply_when_extending(self):
		self.assertEqual(
			normalizeEmail("John.Doe@gmail.com", self.options), "johndoe@gmail.com"
		)


class TestProviderOverride(unittest.TestCase):
	def setUp(self):
		self.override = NormalizeOptions(
			providers=[
				ProviderRule(
					id="gmail-strict", domains=["gmail.com"], lowercaseLocal=True
				)
			]
		)

	def test_custom_provider_overrides_builtin(self):
		self.assertEqual(
			normalizeEmail("John.Doe@gmail.com", self.override), "john.doe@gmail.com"
		)

	def test_overriding_provider_id_is_reported(self):
		self.assertEqual(getEmailProvider("a@gmail.com", self.override), "gmail-strict")


class TestReplaceDefaultProviders(unittest.TestCase):
	def setUp(self):
		self.replaced = NormalizeOptions(
			replaceDefaultProviders=True,
			providers=[
				ProviderRule(
					id="only",
					domains=["only.com"],
					subaddressSeparators=["+"],
					lowercaseLocal=True,
				)
			],
		)

	def test_builtins_are_ignored(self):
		self.assertIsNone(getEmailProvider("a@gmail.com", self.replaced))

	def test_unmatched_domains_use_conservative_default(self):
		self.assertEqual(
			normalizeEmail("John.Doe+x@gmail.com", self.replaced),
			"John.Doe+x@gmail.com",
		)

	def test_supplied_provider_still_applies(self):
		self.assertEqual(
			normalizeEmail("John+x@only.com", self.replaced), "john@only.com"
		)


class TestDefaultRule(unittest.TestCase):
	def setUp(self):
		self.with_default = NormalizeOptions(
			defaultRule=LocalPartRules(lowercaseLocal=True, subaddressSeparators=["+"])
		)

	def test_default_rule_applies_to_unknown_domains(self):
		self.assertEqual(
			normalizeEmail("John+tag@example.com", self.with_default),
			"john@example.com",
		)

	def test_default_rule_does_not_override_matched_provider(self):
		self.assertEqual(
			normalizeEmail("john+tag@yahoo.com", self.with_default),
			"john+tag@yahoo.com",
		)


class TestDomainCasingAndSameEmail(unittest.TestCase):
	def test_lowercase_domain_can_be_disabled(self):
		self.assertEqual(
			normalizeEmail("user@Example.COM", NormalizeOptions(lowercaseDomain=False)),
			"user@Example.COM",
		)

	def test_is_same_email_respects_options(self):
		same_opts = NormalizeOptions(
			defaultRule=LocalPartRules(subaddressSeparators=["+"])
		)
		self.assertTrue(isSameEmail("a+x@example.com", "a+y@example.com", same_opts))

	def test_without_options_the_tags_differ(self):
		self.assertFalse(isSameEmail("a+x@example.com", "a+y@example.com"))


class TestRegistryCaching(unittest.TestCase):
	def test_same_options_object_is_consistent_across_calls(self):
		options = NormalizeOptions(
			providers=[
				ProviderRule(
					id="corp",
					domains=["corp.example"],
					canonicalDomain="corp.example",
					lowercaseLocal=True,
					subaddressSeparators=["+"],
				)
			]
		)
		# Repeated calls reuse the memoized registry and stay correct.
		for _ in range(3):
			self.assertEqual(
				normalizeEmail("John+x@corp.example", options),
				"john@corp.example",
			)
			self.assertEqual(getEmailProvider("a@corp.example", options), "corp")
		# isSameEmail normalizes twice with the same options object.
		self.assertTrue(
			isSameEmail("John+a@corp.example", "john+b@corp.example", options)
		)

	def test_distinct_options_objects_do_not_bleed(self):
		opts_a = NormalizeOptions(
			providers=[ProviderRule(id="a", domains=["shared.example"])]
		)
		opts_b = NormalizeOptions(
			providers=[ProviderRule(id="b", domains=["shared.example"])]
		)
		self.assertEqual(getEmailProvider("x@shared.example", opts_a), "a")
		self.assertEqual(getEmailProvider("x@shared.example", opts_b), "b")
		# Re-querying the first must still return its own provider.
		self.assertEqual(getEmailProvider("x@shared.example", opts_a), "a")


if __name__ == "__main__":
	unittest.main()
