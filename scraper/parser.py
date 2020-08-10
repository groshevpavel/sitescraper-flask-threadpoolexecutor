from urllib.parse import urlparse

import lxml.html


def yield_links(html):
    parsed = lxml.html.document_fromstring(html)

    for element, attribute, link, pos in parsed.body.iterlinks():
        yield {
            'element': element,
            'attribute': attribute,
            'link': link,
            'pos': pos,
        }


EXTENSIONS_TO_STORE = (
    '.html', '.css', '.js',
    '.jpeg', '.jpg', '.png', '.gif', '.webp'
    '.svg',
    '.ogg', '.webm',
)


def determine_link(url: str) -> bool:
    """Determine is new page link or file that we need to save"""
    return any(url.endswith(e) for e in EXTENSIONS_TO_STORE)


def get_link_filename(url: str) -> str:
    return urlparse(url).path
