import inspect
from itertools import combinations


class QueryBuilder():
    """ Base query builder """

    def build(self, terms: list):
        raise NotImplementedError(
            f"{inspect.stack()[0][3]} is not implemented")


class DefaultQueryBuilder(QueryBuilder):
    """ Default query builder """

    def build(self, terms: list):
        yield ' '.join(list(map(lambda t: f'"{t}"' if ' ' in t else t, terms)))


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

    @classmethod
    def create(cls, name: str):
        """
        Creates a builder by name, if builder is not defined the
        default query builder will be returned.
        """
        if name not in cls.query_builders:
            return cls.query_builders['default']()
        return cls.query_builders[name]()
