import re

from friendlylog import colored_logger as log


class Expander:
    STOP_TERMS = ['AND', 'OR', 'NOT']

    def dna_change(term, match):
        try:
            var1 = f"{match.group('number')}{match.group('ref')}>{match.group('alt')}"
            var2 = f"{match.group('number')}{match.group('ref')}->{match.group('alt')}"
            var3 = f"{match.group('number')}{match.group('ref')}-->{match.group('alt')}"
            var4 = f"{match.group('number')}{match.group('ref')}/{match.group('alt')}"
            return [var1, var2, var3, var4]
        except KeyError as ke:
            log.warning(ke)
            return [term]

    def protein_change_1_letter(term, match):
        aa_code = {
            "A": "Ala", "C": "Cys", "D": "Asp", "E": "Glu", "F": "Phe",
            "G": "Gly", "H": "His", "I": "Ile", "K": "Lys", "L": "Leu",
            "M": "Met", "N": "Asn", "P": "Pro", "Q": "Gln", "R": "Arg",
            "S": "Ser", "T": "Thr", "V": "Val", "W": "Trp", "Y": "Tyr",
            "*": "Ter", "X": "Ter"
        }
        try:
            return [f"{aa_code[match.group('prefix')]}{match.group('number')}{aa_code[match.group('postfix')]}"]
        except KeyError as ke:
            log.warning(ke)
            return [term]

    def protein_change_3_letter(term, match):
        aa_code = {
            "Ala": "A", "Cys": "C", "Asp": "D", "Glu": "E", "Phe": "F",
            "Gly": "G", "His": "H", "Ile": "I", "Lys": "K", "Leu": "L",
            "Met": "M", "Asn": "N", "Pro": "P", "Gln": "Q", "Arg": "R",
            "Ser": "S", "Thr": "T", "Val": "V", "Trp": "W", "Tyr": "Y",
            "Ter": "*", "*": "X"
        }
        try:
            return [f"{aa_code[match.group('prefix')]}{match.group('number')}{aa_code[match.group('postfix')]}"]
        except KeyError as ke:
            log.warning(ke)
            return [term]

    matchers = [
        {
            'regex': re.compile(r'(?P<prefix>\D{1})(?P<number>\d+)(?P<postfix>\D{1})'),
            'translator': protein_change_1_letter
        },
        {
            'regex': re.compile(r'(?:p\.)?(?P<prefix>[A-z]{3})(?P<number>\d+)(?P<postfix>[A-z]{3}|\*)'),
            'translator': protein_change_3_letter
        },
        {
            'regex': re.compile(r'(?:c\.)?(?P<number>[0-9-*]+)(?P<ref>[ACTGN]{1})>(?P<alt>[ACTGN]{1})'),
            'translator': dna_change
        }
    ]

    @classmethod
    def term_cleanup(cls, terms):
        for idx, term in enumerate(terms):
            terms[idx] = re.sub(r'(^p\.|^c\.)', '', term)
        return terms

    @classmethod
    def expand(cls, terms: list):
        old = []
        new = []
        for term in terms:
            term = term.strip()
            term = term.replace('"', '').replace("'", '')
            old.append(term)
            new.append(term)
            for matcher in cls.matchers:
                match = matcher['regex'].match(term)
                if match:
                    terms = matcher['translator'](term, match)
                    new += terms
                    new = cls.term_cleanup(new)
                    break
            log.debug(f"Expanded: term={term}: {new}")
        return old, list(set(new))
