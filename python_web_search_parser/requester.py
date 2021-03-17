from sys import stdout
import re
from json import loads
import traceback

import requests
from friendlylog import colored_logger as log


class Requester():
    @staticmethod
    def get(url: str, **kwargs):
        log.info(f"Request url={url} args={kwargs}")
        try:
            res = requests.get(url, params=kwargs, timeout=5)
            log.debug(f"Response code={res.status_code}")
            if res.ok:
                with open(f"{url.replace('/', '_')}.html", 'w') as f:
                    f.write(res.text)
                return res.text
            else:
                log.error(res.text)
                return None
        except requests.RequestException as ex:
            log.error(ex)


class MultistageRequester():
    RE_PARSE_PARAM = re.compile(
        r'(?:(?P<action>[^\(]+)\((?P<attributes>[^\)]*)\):|^)?(?P<content>.+)$')

    @classmethod
    def get(cls, urls: list):
        if not isinstance(urls, list):
            raise TypeError('urls is not of type list')
        response = None
        for url in urls:
            params = url['params']
            for param, value in params.items():
                match = cls.RE_PARSE_PARAM.match(str(value))
                if match:
                    action = match.group('action')
                    attributes = match.group('attributes')
                    content = match.group('content')
                    log.debug(
                        f"params: action={action}, attributes={attributes}, content={content}")
                    if action == 'eval':
                        if attributes == 'json':
                            if response:
                                log.debug(f"response={response}")
                                json = loads(response)
                                log.debug(f"json={json}")
                                try:
                                    content = eval(content)
                                except Exception as ex:
                                    log.warning(
                                        f"Cannot evaluate {content}: {ex}")
                                    traceback.print_exc(file=stdout)
                                    content = ''
                params[param] = content
            response = Requester.get(url['url'], **params)
            if not response:
                break
        return response
