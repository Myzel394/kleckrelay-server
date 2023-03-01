from datetime import datetime

import lxml.html
import PIL
import requests
from fastapi import HTTPException
from lxml.etree import _Element, XMLSyntaxError
from pyquery import PyQuery as pq

from app.email_report_data import (
    EmailReportData, EmailReportExpandedURLData, EmailReportProxyImageData,
    EmailReportSinglePixelImageTrackerData,
)
from app.models import EmailAlias
from app.models.constants.alias import PROXY_USER_AGENT_STRING_MAP
from app.utils.image import create_image_url, download_image, save_image
from email_utils.handlers import check_is_url_a_tracker

__all__ = [
    "convert_images",
    "remove_single_pixel_image_trackers",
    "expand_shortened_urls"
]


def convert_images(
    report: EmailReportData,
    /,
    alias: EmailAlias,
    html: str,
) -> str:
    try:
        d = pq(lxml.html.fromstring(html))
    except XMLSyntaxError as error:
        return html

    for image in d("img"):  # type: _Element
        source = image.attrib["src"]
        image.attrib["data-kleckrelay-original-src"] = source

        file = None

        try:
            file = save_image(
                url=source,
                alias=alias,
            )
        except (HTTPException, PIL.UnidentifiedImageError, ValueError):
            pass

        url = create_image_url(
            original_url=source,
            alias_id=alias.id,
            file=file,
        )
        image.attrib["src"] = url

        report.proxied_images.append(
            EmailReportProxyImageData(
                url=source,
                created_at=datetime.utcnow(),
                server_url=url,
            )
        )

    return d.outer_html()


def check_is_single_pixel_image(image: _Element) -> bool:
    return str(image.attrib.get("width")) == "0" \
        or str(image.attrib.get("height")) == "0" \
           or (str(image.attrib.get("width")) == "1" and str(image.attrib.get("height") == "1"))


def remove_single_pixel_image_trackers(report: EmailReportData, /, html: str) -> str:
    try:
        d = pq(lxml.html.fromstring(html))
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

    return d.outer_html()


def expand_url(url: str, user_agent: str) -> str:
    response = requests.get(url, headers={"User-Agent": user_agent})

    return response.url


def expand_shortened_urls(
    report: EmailReportData,
    /,
    alias: EmailAlias,
    html: str
) -> str:
    try:
        d = pq(lxml.html.fromstring(html))
    except XMLSyntaxError:
        return html

    for link in d("a"):  # type: _Element
        source = link.attrib["href"]
        link.attrib["data-kleckrelay-original-href"] = source
        url = expand_url(
            source,
            PROXY_USER_AGENT_STRING_MAP[alias.proxy_user_agent]
        )
        link.attrib["href"] = url

        report.expanded_urls.append(
            EmailReportExpandedURLData(
                original_url=source,
                expanded_url=url,
                query_trackers=[],
            )
        )

    return d.outer_html()
