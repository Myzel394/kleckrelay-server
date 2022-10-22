from lxml import etree
from pyquery import PyQuery as pq

from app import life_constants
from app.constants import ROOT_DIR
from app.email_report_data import EmailReportData
from email_utils import html_handler


def test_can_convert_images(
    db,
    create_user,
    create_random_alias
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user, pref_proxy_images=True)

    html = (ROOT_DIR / "explorative_tests" / "proxy_images.html").read_text()

    report = EmailReportData(
        mail_from="from@example.com",
        mail_to="to@example.com",
        subject="Awesome Subject here",
        message_id="",
        report_id="",
    )
    new_html = html_handler.convert_images(db, report, alias=alias, html=html)

    assert html != new_html, "HTML should have changed."
    d = pq(etree.fromstring(new_html))
    img = d.find("img")[0]
    assert img.get("src").startswith(f"https://{life_constants.API_DOMAIN}/image-proxy"), \
        "Image's `src` should have changed."
    assert len(report.proxied_images) == 1, "There should be one proxied images."
    # Check if call doesn't throw an error
    report.as_dict()


def test_can_remove_single_pixel_tracker_images_by_url():
    html = (ROOT_DIR / "explorative_tests" / "image_tracker_url.html").read_text()

    report = EmailReportData(
        mail_from="from@example.com",
        mail_to="to@example.com",
        subject="Awesome Subject here",
        message_id="",
        report_id="",
    )
    new_html = html_handler.remove_single_pixel_image_trackers(report, html=html)

    assert html != new_html, "HTML should have changed."
    d = pq(etree.fromstring(new_html))
    images = d.find("img")
    assert len(images) == 0, "There should be no images left."


def test_can_remove_single_pixel_tracker_image_by_size():
    html = (ROOT_DIR / "explorative_tests" / "single_width_image.html").read_text()

    report = EmailReportData(
        mail_from="from@example.com",
        mail_to="to@example.com",
        subject="Awesome Subject here",
        message_id="",
        report_id="",
    )
    new_html = html_handler.remove_single_pixel_image_trackers(report, html=html)

    assert html != new_html, "HTML should have changed."
    d = pq(etree.fromstring(new_html))
    images = d.find("img")
    assert len(images) == 0, "There should be no images left."
