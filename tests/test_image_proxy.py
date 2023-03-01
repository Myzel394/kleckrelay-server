from urllib.parse import urlparse

import lxml.html
from pyquery import PyQuery as pq
from sqlalchemy.orm import Session

from app.constants import ROOT_DIR
from app.email_report_data import EmailReportData
from email_utils import content_handler


def test_can_proxy_image(
    db: Session,
    create_user,
    create_random_alias,
    client,
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user, pref_proxy_images=True)

    html = (ROOT_DIR / "explorative_tests" / "outside_image.html").read_text()

    report = EmailReportData(
        mail_from="from@example.com",
        mail_to="to@example.com",
        subject="Awesome Subject here",
        message_id="",
        report_id="",
    )
    new_html = content_handler.convert_images(report, alias=alias, html=html)

    d = pq(lxml.html.fromstring(new_html))
    img = d.find("img")[0]
    new_url = img.get("src")
    # New url contains full URL to the image, but we need to remove the domain
    result = urlparse(new_url)
    path = result.path + "?" + result.query

    response = client.get(
        path,
    )

    assert response.status_code == 200, f"Status code should be 200 but is {response.status_code}."
