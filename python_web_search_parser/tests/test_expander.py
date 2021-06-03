from unittest import TestCase
from python_web_search_parser.expander import Expander


class ExpanderTest(TestCase):
    def test_expander(self):
        """Test basic expander behavior"""
        old, new = Expander.expand(['bla', 'blu'])
        self.assertEqual(['bla', 'blu'], old)
        self.assertEqual(['bla', 'blu'], new)

    def test_expander_whitespace(self):
        """Test expander with terms including whitespaces"""
        old, new = Expander.expand(['bla bla', 'blu li'])
        self.assertEqual(['bla bla', 'blu li'], old)
        self.assertEqual(['bla bla', 'blu li'], new)
