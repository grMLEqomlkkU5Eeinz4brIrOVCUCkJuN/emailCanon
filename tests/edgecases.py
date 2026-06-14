import unittest

from emailcanon import normalizeEmail, normalizeEmailDetailed


class TestUnknownDomains(unittest.TestCase):
	def test_domain_lowercased_local_case_preserved(self):
		self.assertEqual(normalizeEmail("John.Doe@Example.COM"), "John.Doe@example.com")

	def test_tags_not_stripped_by_default(self):
		self.assertEqual(normalizeEmail("john+tag@example.com"), "john+tag@example.com")

	def test_dots_not_removed_by_default(self):
		self.assertEqual(normalizeEmail("john.doe@example.com"), "john.doe@example.com")


class TestQuotedLocalParts(unittest.TestCase):
	def test_quoted_local_part_is_preserved(self):
		self.assertEqual(
			normalizeEmail('"John..Doe+x"@gmail.com'), '"John..Doe+x"@gmail.com'
		)


class TestSubaddressEdgeCases(unittest.TestCase):
	def test_separator_at_index_zero_is_ignored(self):
		self.assertEqual(normalizeEmail("+tag@gmail.com"), "+tag@gmail.com")

	def test_only_first_separator_is_the_cut_point(self):
		self.assertEqual(normalizeEmail("user+a+b@outlook.com"), "user@outlook.com")

	def test_empty_subaddress_is_none(self):
		result = normalizeEmailDetailed("user+@gmail.com")
		self.assertIsNone(result.subaddress)
		self.assertEqual(result.normalized, "user@gmail.com")


class TestInputHandling(unittest.TestCase):
	def test_surrounding_whitespace_is_trimmed(self):
		self.assertEqual(normalizeEmail("   user@example.com  "), "user@example.com")

	def test_address_is_split_on_the_last_at(self):
		result = normalizeEmailDetailed('"a@b"@gmail.com')
		self.assertEqual(result.domain, "gmail.com")
		self.assertEqual(result.local, '"a@b"')

	def test_non_string_input_raises_type_error(self):
		with self.assertRaises(TypeError):
			normalizeEmail(None)


class TestValidityFlag(unittest.TestCase):
	def test_input_without_at_is_invalid(self):
		self.assertFalse(normalizeEmailDetailed("not-an-email").valid)

	def test_invalid_input_returned_unchanged(self):
		self.assertEqual(
			normalizeEmailDetailed("not-an-email").normalized, "not-an-email"
		)

	def test_empty_local_part_is_invalid(self):
		self.assertFalse(normalizeEmailDetailed("@example.com").valid)

	def test_empty_domain_is_invalid(self):
		self.assertFalse(normalizeEmailDetailed("user@").valid)

	def test_well_formed_address_is_valid(self):
		self.assertTrue(normalizeEmailDetailed("user@example.com").valid)


class TestStructuredResult(unittest.TestCase):
	def test_fields_are_correct(self):
		detailed = normalizeEmailDetailed("John.Doe+promo@gmail.com")
		self.assertEqual(detailed.normalized, "johndoe@gmail.com")
		self.assertEqual(detailed.local, "johndoe")
		self.assertEqual(detailed.domain, "gmail.com")
		self.assertEqual(detailed.providerId, "gmail")
		self.assertEqual(detailed.subaddress, "promo")
		self.assertTrue(detailed.valid)

	def test_subaddress_is_none_when_absent(self):
		self.assertIsNone(normalizeEmailDetailed("john@gmail.com").subaddress)

	def test_provider_id_is_none_for_unknown_domains(self):
		self.assertIsNone(normalizeEmailDetailed("john@example.com").providerId)


if __name__ == "__main__":
	unittest.main()
