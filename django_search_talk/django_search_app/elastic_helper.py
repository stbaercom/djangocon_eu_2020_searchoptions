import datetime
import logging

import requests

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


def ecommand(verb, path, data=None):
    EHOST = "localhost"
    EPORT = 9200
    url = f"http://{EHOST}:{EPORT}/{path}"
    kwargs = {}
    if data:
        kwargs["json"] = data
    reply = requests.request(verb, url, **kwargs)
    if not reply.ok:
        raise Exception(f"{reply.status_code} {reply.text}")

    result = reply.json()
    return result


def get(path, data=None):
    return ecommand("GET", path, data)


def put(path, data=None):
    return ecommand("PUT", path, data)


def post(path, data=None):
    return ecommand("POST", path, data)


def delete(path, data=None):
    return ecommand("DELETE", path, data)


def create_index(index_name):
    put(index_name)

    settings = {
        "analysis": {
            "filter": {
                "englishStopWords": {
                    "type": "stop",
                    "stopwords": "_english_"
                }
            },
            "analyzer": {
                "reviewAnalyzer": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "englishStopWords"
                    ]
                }
            }
        }
    }

    post(f"{index_name}/_close")
    put(f"{index_name}/_settings", settings)
    post(f"{index_name}/_open")

    mapping = {'properties':
                   {'name': {'type': 'keyword'},
                    'productId': {'type': 'keyword'},
                    'review_help_help': {'type': 'long'},
                    'review_help_total': {'type': 'long'},
                    'review_score': {'type': 'float'},
                    'review_summary': {
                        'type': 'text',
                        'analyzer': "reviewAnalyzer",
                        'search_analyzer': "reviewAnalyzer"
                    },
                    'review_text': {
                        'type': 'text',
                        'analyzer': "reviewAnalyzer",
                        'search_analyzer': "reviewAnalyzer"
                    },
                    'review_time': {'type': 'date'},
                    'userId': {'type': 'keyword'}
                    }
               }
    put(f"{index_name}/_mapping", mapping)


def delete_index(index_name):
    return delete(index_name)


def write_docs(index_name, docs):
    for i, (eid, doc) in enumerate(docs.items()):
        if i % 100 == 0:
            logging.info(f"Elastic {i} / {len(docs)}")
        entry = {}
        for k, v in doc.items():
            if isinstance(v, (datetime.date, datetime.datetime)):
                v = v.isoformat()
            entry[k] = v
        put(f"{index_name}/_doc/{eid}", entry)


def search(index_name, qstring):
    search = {
        "query": {
            "term": {
                "review_text": qstring
            }
        }
    }
    return post(f"{index_name}/_search", search)


def multi_search(index_name, qstring):
    search = {
        "query": {
            "multi_match": {
                "query": qstring,
                "fields": ["review_text", "review_summary"]
            }
        }
    }
    return post(f"{index_name}/_search", search)


def multi_search_facets(index_name, qstring, size):
    query = {
            "multi_match": {
                "query": qstring,
                "fields": ["review_text", "review_summary"]
            }
        }
    return inner_search(index_name, query,size=size)


def multi_search_facets_filter(index_name, qstring, qfilter={}):
    query_part = {
            "multi_match": {
                "query": qstring,
                "fields": ["review_text", "review_summary"]
            }
        }

    if qfilter:
        name_map = {
            "product":"productId",
            "user": "userId",
            "score": "review_score"
        }

        filter_part =  [{'term': {name_map[k]:v}} for k,v in qfilter.items()]

        query = {
            'bool': {
                'must': query_part,
                'filter': filter_part
            }
        }
    else:
        query = query_part

    result =  inner_search(index_name, query)
    return result



def inner_search(index_name, query,size):
    search = {
        "query": query,
        "stored_fields": [],
        "size": size,
        "aggs": {
            "score": {
                "terms": {
                    "field": "review_score",
                    "order": {"_count": "desc"}
                }
            },
            "user": {
                "terms": {
                    "field": "userId",
                    "order": {"_count": "desc"}
                }
            },
            "product": {
                "terms": {
                    "field": "productId",
                    "order": {"_count": "desc"}
                }
            }
        }
    }
    return post(f"{index_name}/_search", search)


def write_elastic(index_name, docs):
    try:
        delete_index(index_name)
    except:
        pass
    create_index(index_name)
    write_docs(index_name, docs)


def main():
    result = multi_search_facets("reviews", "good")
    a = 1


if __name__ == '__main__':
    main()
