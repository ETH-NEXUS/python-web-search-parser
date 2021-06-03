import inspect
from itertools import combinations


class QueryBuilder():
    """ Base query builder """

    def build(self, must_terms: list, optional_terms: list, and_op: str = 'AND', or_op: str = 'OR'):
        raise NotImplementedError(
            f"{inspect.stack()[0][3]} is not implemented")


class DefaultQueryBuilder(QueryBuilder):
    """ Default query builder """

    def build(self, must_terms: list, optional_terms: list, and_op='AND', or_op='OR'):
        # Creates a query like 'term[0] AND term[1]'
        query = ''
        if must_terms and len(must_terms) > 0:
            must = f" {and_op} ".join(
                list(map(lambda t: f'"{t}"' if ' ' in t else t, must_terms)))
            if len(must_terms) > 1:
                query += f"({must})"
            else:
                query += f"{must}"
        if optional_terms and len(optional_terms) > 0:
            optional = f" {or_op} " .join(
                list(map(lambda t: f'"{t}"' if ' ' in t else t, optional_terms)))
            if query:
                query += f" {and_op} ({optional})"
            else:
                query += f"{optional}"
        yield query


class GoogleScholarQueryBuilder(QueryBuilder):
    """ Google Scholar query builder """

    def build(self, terms: list):
        combis = list(combinations(terms, 2))
        for combi in combis:
            yield ' '.join(list(map(lambda t: f'"{t}"' if ' ' in t else t, combi)))


class QueryBuilderFactory():
    """ Factory to create the required query builder """

    query_builders = {
        'default': DefaultQueryBuilder,
        'google_scholar': GoogleScholarQueryBuilder
    }

    @ classmethod
    def create(cls, name: str):
        """
        Creates a builder by name, if builder is not defined the
        default query builder will be returned.
        """
        if name not in cls.query_builders:
            return cls.query_builders['default']()
        return cls.query_builders[name]()
