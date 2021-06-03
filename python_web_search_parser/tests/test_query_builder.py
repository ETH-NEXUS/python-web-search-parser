from unittest import TestCase
from python_web_search_parser.query_builder import DefaultQueryBuilder


class QueryBuilderTest(TestCase):
    def test_default_query_builder_must_optional_list(self):
        """Test the default query builder with a list of must as well as a list of optional terms"""
        query_builder = DefaultQueryBuilder()
        for query in query_builder.build(must_terms=['MT1', 'MT2'], optional_terms=[
                'OT11', 'OT12', 'OT2']):
            self.assertEqual(
                '(MT1 AND MT2) AND (OT11 OR OT12 OR OT2)', query)

    def test_default_query_builder_must_optional_list_with_different_operators(self):
        """Test the default query builder with a list of must as well as a list of optional terms with different operators"""
        query_builder = DefaultQueryBuilder()
        for query in query_builder.build(must_terms=['MT1', 'MT2'], optional_terms=[
                'OT11', 'OT12', 'OT2'], and_op='&', or_op='|'):
            self.assertEqual(
                '(MT1 & MT2) & (OT11 | OT12 | OT2)', query)

    def test_query_builder_with_no_must(self):
        query_builder = DefaultQueryBuilder()
        for query in query_builder.build(must_terms=[], optional_terms=[
                'OT11', 'OT12', 'OT2']):
            self.assertEqual(
                'OT11 OR OT12 OR OT2', query)

    def test_query_builder_with_one_must(self):
        query_builder = DefaultQueryBuilder()
        for query in query_builder.build(must_terms=['M1'], optional_terms=[
                'OT11', 'OT12', 'OT2']):
            self.assertEqual(
                'M1 AND (OT11 OR OT12 OR OT2)', query)
