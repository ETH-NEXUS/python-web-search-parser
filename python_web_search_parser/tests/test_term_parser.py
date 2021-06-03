from unittest import TestCase
from python_web_search_parser.term_parser import TermParser


class TermParserTest(TestCase):
    def test_term_parser(self):
        must, optional = TermParser.parse('M1! O1 O2 M2!')
        self.assertEqual(must, ['M1', 'M2'])
        self.assertEqual(optional, ['O1', 'O2'])
