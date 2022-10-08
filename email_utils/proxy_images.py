from lxml import etree
from lxml.etree import _Element, XMLSyntaxError
from pyquery import PyQuery as pq
from sqlalchemy.orm import Session

from app.controllers.image_proxy import create_image_proxy
from app.models import EmailAlias

__all__ = [
    "convert_images",
]


def convert_images(
    db: Session,
    /,
    alias: EmailAlias,
    html: str,
) -> str:
    try:
        d = pq(etree.fromstring(html))
    except XMLSyntaxError:
        return html

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]
        image.attrib["data-kleckrelay-original-source"] = source
        image_proxy = create_image_proxy(db, alias=alias, url=source)

        image.attrib["src"] = image_proxy.generate_url(source)

    return d.html()
