from lxml import etree
from lxml.etree import _Element, XMLSyntaxError
from pyquery import PyQuery as pq
from sqlalchemy.orm import Session

from app.controllers.image_proxy import create_image_proxy
from app.email_report_data import (
    EmailReportData, EmailReportProxyImageData,
    EmailReportSinglePixelImageTrackerData,
)
from app.models import EmailAlias
from email_utils.trackers_handler import check_is_url_a_tracker

__all__ = [
    "convert_images",
    "remove_single_pixel_image_trackers",
]


def convert_images(
    db: Session,
    report: EmailReportData,
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

        report.proxied_images.append(
            EmailReportProxyImageData(
                url=source,
                image_proxy_id=image_proxy.id,
            )
        )

    return d.html()


def check_is_single_pixel_image(image: _Element) -> bool:
    return str(image.attrib.get("width")) == "0" \
        or str(image.attrib.get("height")) == "0" \
           or (str(image.attrib.get("width")) == "1" and str(image.attrib.get("height") == "1"))


def remove_single_pixel_image_trackers(report: EmailReportData, /, html: str) -> str:
    try:
        d = pq(etree.fromstring(html))
    except XMLSyntaxError:
        return html

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]

        tracker = {}

        if check_is_single_pixel_image(image) \
                or (tracker := check_is_url_a_tracker(source)) is not None:
            report.single_pixel_images.append(
                EmailReportSinglePixelImageTrackerData(
                    source=source,
                    tracker_name=tracker.get('name'),
                    tracker_url=tracker.get('url'),
                )
            )

            image.getparent().remove(image)

    return d.html()
