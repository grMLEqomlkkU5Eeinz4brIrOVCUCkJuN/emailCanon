import unittest

from emailcanon import isSameEmail, normalizeEmail


class TestGmail(unittest.TestCase):
	def test_removes_dots_from_local_part(self):
		self.assertEqual(normalizeEmail("john.doe@gmail.com"), "johndoe@gmail.com")

	def test_strips_plus_subaddressing(self):
		self.assertEqual(
			normalizeEmail("johndoe+newsletter@gmail.com"), "johndoe@gmail.com"
		)

	def test_lowercases_local_part(self):
		self.assertEqual(normalizeEmail("JohnDoe@gmail.com"), "johndoe@gmail.com")

	def test_collapses_googlemail_to_gmail(self):
		self.assertEqual(normalizeEmail("john.doe@googlemail.com"), "johndoe@gmail.com")

	def test_dots_tags_case_alias_and_trimming_combine(self):
		self.assertEqual(
			normalizeEmail("  John.Doe+promo@GoogleMail.com "), "johndoe@gmail.com"
		)

	def test_dotted_and_plussed_variants_are_same_mailbox(self):
		self.assertTrue(
			isSameEmail("j.o.h.n@gmail.com", "john+anything@googlemail.com")
		)


if __name__ == "__main__":
	unittest.main()
