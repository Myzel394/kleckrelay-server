from email.message import EmailMessage

from aiosmtpd.smtp import Envelope

from app import constants
from app.constants import ROOT_DIR
from app.controllers.server_statistics import get_server_statistics
from email_utils.handler import handle


def test_can_create_statistics(
    create_user,
    create_random_alias,
    db,
    client,
):
    previous_statistics = client.get("/v1/server/statistics").json()
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user)

    message = EmailMessage()
    envelope = Envelope()
    html = (ROOT_DIR / "explorative_tests" / "image_tracker_url.html").read_text()
    envelope.mail_from = "outside@example.com"
    envelope.rcpt_tos = [alias.address]
    message.set_payload(html)

    response = handle(
        envelope=envelope,
        message=message,
    )

    new_statistics = client.get("/v1/server/statistics").json()

    assert previous_statistics["sent_emails_amount"] != new_statistics["sent_emails_amount"]
    assert previous_statistics["trackers_removed_amount"] != new_statistics[
        "trackers_removed_amount"]
    assert previous_statistics["proxied_images_amount"] == new_statistics[
        "proxied_images_amount"], "proxied images amount should not have changed"
    assert previous_statistics["users_amount"] != new_statistics["users_amount"]
    assert previous_statistics["aliases_amount"] != new_statistics["aliases_amount"]
    assert previous_statistics["app_version"] == constants.APP_VERSION
