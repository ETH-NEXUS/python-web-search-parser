from tssplit import tssplit


class TermParser():
    @classmethod
    def parse(cls, terms: str):
        parsed_terms = tssplit(
            terms, quote='"', delimiter=' ')
        must = []
        optional = []
        for term in parsed_terms:
            if term.endswith('!'):
                must.append(term[:-1])
            else:
                optional.append(term)
        return must, optional
