from lxml import etree
from lxml.etree import _Element
from pyquery import PyQuery as pq
from sqlalchemy.orm import Session

from app.controllers.image_proxy import create_image_proxy

__all__ = [
    "convert_images",
]


def convert_images(db: Session, /, html: str) -> str:
    d = pq(etree.fromstring(html))

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]
        image.attrib["data-kleckrelay-original-source"] = source
        image_proxy = create_image_proxy(db, source)

        image.attrib["src"] = image_proxy.generate_url(source)

    return d.html()
