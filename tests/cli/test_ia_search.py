import os
import sys
inc_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, inc_path)
try:
    import ujson as json
except ImportError:
    import json
from copy import deepcopy

import responses

from internetarchive.cli import ia


protocol = 'https:'


ROOT_DIR = os.getcwd()
TEST_JSON_FILE = os.path.join(ROOT_DIR, 'tests/data/advanced_search_response.json')
with open(TEST_JSON_FILE) as fh:
    TEST_SEARCH_RESPONSE = fh.read()
TEST_JSON_SCRAPE_FILE = os.path.join(ROOT_DIR, 'tests/data/scrape_response.json')
with open(TEST_JSON_SCRAPE_FILE) as fh:
    TEST_SCRAPE_RESPONSE = fh.read()


def test_ia_search_itemlist(capsys):
    with responses.RequestsMock() as rsps:
        url1 = ('{0}//archive.org/services/search/beta/scrape.php'
                '?q=collection%3Aattentionkmartshoppers'
                '&fields=identifier&size=10000'.format(protocol))
        url2 = ('{0}//archive.org/services/search/beta/scrape.php'
                '?q=collection%3Aattentionkmartshoppers&fields=identifier'
                '&cursor=W3siaWRlbnRpZmllciI6IjE5NjEtTC0wNTkxNCJ9XQ%3D%3D'
                '&size=10000'.format(protocol))
        rsps.add(responses.GET, url1,
                 body=TEST_SCRAPE_RESPONSE,
                 status=200,
                 match_querystring=True)
        _j = json.loads(TEST_SCRAPE_RESPONSE)
        del _j['cursor']
        _r = json.dumps(_j)
        rsps.add(responses.GET, url2,
                 body=_r,
                 status=200,
                 match_querystring=True)

        sys.argv = ['ia', 'search', 'collection:attentionkmartshoppers', '--itemlist']
        try:
            ia.main()
        except SystemExit as exc:
            assert not exc.code

    out, err = capsys.readouterr()
    j = json.loads(TEST_SEARCH_RESPONSE)
    assert len(out.split()) == 200


def test_ia_search_num_found(capsys):
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        url = ('{0}//archive.org/services/search/beta/scrape.php'
               '?q=collection%3Anasa&total_only=true'.format(protocol))
        url = ('{0}//archive.org/advancedsearch.php?'
               'q=collection%3Anasa&output=json&rows=0'.format(protocol))
        rsps.add(responses.GET, url,
                 body='{"items":[],"count":0,"total":50}',
                 status=200,
                 match_querystring=True)

        sys.argv = ['ia', 'search', 'collection:nasa', '--num-found']
        try:
            ia.main()
        except SystemExit as exc:
            assert not exc.code

    out, err = capsys.readouterr()
    assert out == '50\n'
