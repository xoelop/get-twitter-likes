import re

import requests
import requests_cache
from lxml import etree, html

def get_url_title_description(url: str, parse_url: bool = True) -> dict:
    default_result = {
        'title': '',
        'description': ''
    }
    if not url or not parse_url:
        return default_result
    try:
        session = requests_cache.CachedSession(backend='sqlite', expire_after=700000)
        response = session.get(url, timeout=3)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', 'text/html')
        if 'html' in content_type.lower():
            try:
                tree = html.document_fromstring(response.content.decode('UTF-8', 'ignore'))
                result = {
                    'title': get_title(tree),
                    'description': get_description(tree)
                }
            except (etree.ParserError, ValueError) as e:
                return default_result
        else:
            result = default_result

    except requests.exceptions.RequestException as e:
        return default_result
    return result


def get_title(tree) -> str:
    xpaths = [
        '//title/text()[1]',
        "//meta[@name='title']/@content",
        "//meta[@property='og:title']/@content"
    ]
    return get_xpath_results(tree, xpaths)


def get_description(tree) -> str:
    xpaths = [
        "//meta[@name='description']/@content",
        "//meta[@property='og:description']/@content",
    ]
    return get_xpath_results(tree, xpaths)


def get_xpath_results(tree, xpaths) -> str:
    elements = set()
    for xpath in xpaths:
        try:
            xpath_results = tree.xpath(xpath)
            for result in xpath_results:
                elements.add(result)
        except IndexError:
            pass

    elements = list(elements)
    result = ' '.join(elements)
    result = re.sub(r'[\n\r]', ' ', result)
    return result
