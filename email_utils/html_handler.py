from lxml import etree
from lxml.etree import _Element, XMLSyntaxError
from pyquery import PyQuery as pq
from sqlalchemy.orm import Session

from app.controllers.image_proxy import create_image_proxy
from app.models import EmailAlias
from email_utils.trackers_handler import check_is_url_a_tracker

__all__ = [
    "convert_images",
    "remove_single_pixel_image_trackers",
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


def check_is_single_pixel_image(image: _Element) -> bool:
    return str(image.attrib.get("width")) == "0" \
        or str(image.attrib.get("height")) == "0" \
           or (str(image.attrib.get("width")) == "1" and str(image.attrib.get("height") == "1"))


def remove_single_pixel_image_trackers(html: str) -> str:
    try:
        d = pq(etree.fromstring(html))
    except XMLSyntaxError:
        return html

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]

        if check_is_single_pixel_image(image) or check_is_url_a_tracker(source) is not None:
            image.getparent().remove(image)

    return d.html()
