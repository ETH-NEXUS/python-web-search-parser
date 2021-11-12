#!/usr/bin/env python

import logging
from datetime import timedelta as td
from python_web_search_parser.term_parser import TermParser
from timeit import default_timer as timer

import yaml
from envparse import env
from flask import Flask, jsonify, request
from flask_add_ons.logging import colorize_werkzeug
from flask_cors import CORS
from friendlylog import colored_logger as log

from python_web_search_parser.expander import Expander
from python_web_search_parser.parser import Parser
from python_web_search_parser.query_builder import QueryBuilderFactory
from python_web_search_parser.requester import MultistageRequester, Requester


logging.basicConfig(level=logging.DEBUG)
log.setLevel(logging.INFO)
colorize_werkzeug()

app = Flask(__name__)
# CORS(app)
cors = CORS(app, supports_credentials=True, resources={
    r'/api/*': {
        'origins': '*',
        'methods': ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT']
    }
})

app.config['DEFAULT_RENDERERS'] = [
    'flask_api.renderers.JSONRenderer',
    'flask_api.renderers.BrowsableAPIRenderer',
]

app.secret_key = b'Q#G[DK.]uVs9qXW*hWvc32VW!wzL^2A?'

# Add UTF-8 support
app.config['JSON_AS_ASCII'] = False

# disable sorting json keys
app.config['JSON_SORT_KEYS'] = False

log.info("Loading .env")
env.read_envfile()


with open(r'./pwsp.yaml') as file:
    pwsp_config = yaml.load(file, Loader=yaml.FullLoader)


def __get_statistics(items, by='target_source'):
    source_count = {}
    for item in items:
        if item[by] not in source_count:
            source_count[item[by]] = 0
        source_count[item[by]] += 1
    return source_count


def __fix_parameters(params: dict, terms: str, max: int):
    for param in params.keys():
        if params[param] == '$q':
            params[param] = params[param].replace(
                '$q', terms)
        if params[param] == '$max':
            params[param] = params[param].replace(
                '$max', str(max))


def __consolidate_items(items):
    new = []
    for item in items:
        if not next((i for i in new if i['target_source'] == item['target_source'] and i['id'] == item['id']), None):
            new.append(item)
    return new


@app.route('/search/', methods=['GET'])
def search():
    # TODO: to be removed
    with open(r'./pwsp.yaml') as file:
        pwsp_config = yaml.load(file, Loader=yaml.FullLoader)
    ###
    must_terms, optional_terms = TermParser.parse(request.args.get('q'))

    must_terms, expanded_must_terms = Expander.expand(must_terms)
    optional_terms, expanded_optional_terms = Expander.expand(optional_terms)

    expand = request.args.get('expand', 'true') == 'true'
    max = request.args.get('max', 10)
    sources = request.args.get('source').split(
        ',') if request.args.get('source') else None
    start = timer()
    items = []
    for source in pwsp_config['sources']:
        if 'disabled' not in source or not source['disabled']:
            if sources is None or source['source'] in sources:
                log.info(f"Query source {source['source']}")
                queryBuilder = QueryBuilderFactory.create(
                    source['query_builder'] if 'query_builder' in source else 'default')
                for query in queryBuilder.build(
                        must_terms=expanded_must_terms if expand else must_terms,
                        optional_terms=expanded_optional_terms if expand else optional_terms):
                    # multistage
                    if 'urls' in source:
                        for url in source['urls']:
                            __fix_parameters(url['params'], query, max)
                        doc = MultistageRequester.get(
                            source['urls'])
                    else:
                        __fix_parameters(source['params'], query, max)
                        doc = Requester.get(
                            source['url'], **source['params'])
                    for parse in source['parse']:
                        new_items = Parser.parseHtml(
                            doc,
                            highlight=expanded_must_terms +
                            expanded_optional_terms if expand else must_terms + optional_terms,
                            source=source['source'],
                            target_source=source['target_source'] if 'target_source' in source else None,
                            **parse)
                        for item in new_items:
                            item.update({'query': query})
                        items += new_items
    log.info("Finalize...")
    result = {}
    result['source_count_details'] = __get_statistics(items, 'source')

    items = __consolidate_items(items)
    result['count'] = len(items)
    result['source_count'] = __get_statistics(items)
    result['terms'] = must_terms + optional_terms
    result['expanded_terms'] = expanded_must_terms + expanded_optional_terms
    result['expand'] = expand
    end = timer()
    result['took'] = td(seconds=end-start).total_seconds()
    result['items'] = items
    return jsonify(result)


def gunicorn():
    return app


if __name__ == '__main__':
    app.run(host=env('PWSP_HOST', default='localhost'),
            port=env.int('PWSP_PORT', default=9200))
