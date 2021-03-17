from sys import stdout
import re
from typing import OrderedDict
import traceback
from friendlylog import colored_logger as log

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from python_web_search_parser.highlighter import Highlighter


class Parser():
    RE_PARSE_INSTRUCTION = re.compile(
        r'(?:(?P<action>[^\(]+)\((?P<attributes>[^\)]*)\):|^)?(?P<selector>.+)$')

    class record():
        """ The record to return """

        def __init__(self, source, target_source, id, title, link, abstract, details):
            self.dct = OrderedDict()
            self.dct['source'] = source
            self.dct['target_source'] = target_source
            self.dct['id'] = id
            self.dct['title'] = title
            self.dct['link'] = link
            self.dct['abstract'] = abstract
            self.dct['details'] = details

        @staticmethod
        def __clean_value(value):
            return value.replace('\n', '').strip()

        def to_dict(self):
            _dict = {}
            for key in self.dct.keys():
                if isinstance(self.dct[key], str):
                    _dict[key] = self.__clean_value(self.dct[key])
                elif isinstance(self.dct[key], Tag):
                    _dict[key] = self.__clean_value(self.dct[key].text)
                elif isinstance(self.dct[key], ResultSet):
                    if key not in _dict:
                        _dict[key] = []
                    for elt in self.dct[key]:
                        _dict[key].append(self.__clean_value(elt.text))
                else:
                    _dict[key] = '[' + \
                        str(type(self.dct[key])) + '] ' + str(self.dct[key])
            return _dict

    @classmethod
    def __select(cls, elt, selector):
        ret = None
        if selector is not None:
            log.debug(f"Try selector: '{selector}'")
            parts = selector.split('|')
            selector = parts[0]
            filters = None
            if len(parts) > 1:
                filters = parts[1:]
            match = cls.RE_PARSE_INSTRUCTION.match(selector)
            if match:
                action = match.group('action')
                attributes = match.group('attributes')
                selector = match.group('selector')
                log.debug(
                    f"action={action} attributes={attributes} selector={selector}")
                try:
                    if action == 'attr':
                        ret = elt.select(selector)[0][attributes]
                    elif action == 'first':
                        ret = elt.select_one(selector)
                    else:
                        ret = elt.select(selector)
                    if filters:
                        for filter in filters:
                            log.debug(f"Apply filter {filter}")
                            if not isinstance(ret, str):
                                ret = ret.text
                            ret = eval(f"{filter.replace('$','str(ret)')}")
                except Exception as ex:
                    log.error(ex)
                    traceback.print_exc(file=stdout)
                finally:
                    log.debug(f"Found {len(ret) if ret else 0} entries.")
                    log.debug("---")
        if not ret:
            ret = ''
        return ret

    @classmethod
    def parseHtml(cls, doc, highlight=None, parser='html.parser', source='unknown', target_source=None, item=None, id=None, title=None, link=None, abstract=None, details=None):
        try:
            soup = BeautifulSoup(doc, parser)
            log.debug(f"Got results from '{source}'.")
            elements = cls.__select(soup, item)
            records = []
            for elt in elements:
                _source = source
                _target_source = target_source if target_source else source
                _id = cls.__select(elt, id)
                _title = cls.__select(elt, title)
                _link = cls.__select(elt, link)
                _abstract = cls.__select(elt, abstract)
                _details = cls.__select(elt, details)
                rec = cls.record(_source, _target_source, _id, _title,
                                 _link, _abstract, _details).to_dict()
                rec = Highlighter.highlight(
                    rec, ['title', 'abstract'], highlight)
                log.info(f"Record: {rec}")
                records.append(rec)
            return records
        except Exception as ex:
            log.error(ex)
            traceback.print_exc(file=stdout)

    @classmethod
    def parseXml(cls, doc, **kwargs):
        return cls.parseHtml(doc, parser='lxml', **kwargs)
