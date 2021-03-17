import re

from friendlylog import colored_logger as log


class Highlighter():

    @staticmethod
    def highlight(rec: dict, fields: list, terms: list):
        if rec is not None and fields is not None and terms is not None:
            for field in fields:
                if field in rec:
                    for term in terms:
                        rec[field] = re.sub(
                            rf"\b{term}\b", f"<em class='highlight'>{term}</em>", rec[field])
                else:
                    log.warning(
                        f"Field '{field}' is not in highlighting record.")
        return rec
