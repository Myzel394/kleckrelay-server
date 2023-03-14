from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytest
from aiosmtpd.smtp import Envelope

from app import constants
from app.constants import ROOT_DIR
from email_utils import headers
from email_utils.handler import handle


@pytest.mark.asyncio
async def test_can_create_statistics(
    create_user,
    create_random_alias,
    db,
    client,
):
    previous_statistics = client.get("/v1/server/statistics").json()
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user, pref_remove_trackers=True)

    envelope = Envelope()
    envelope.mail_from = "outside@example.com"
    envelope.rcpt_tos = [alias.address]

    html = (ROOT_DIR / "explorative_tests" / "image_tracker_url.html").read_text()
    message = MIMEMultipart("alternative")
    message.attach(MIMEText(html, "html"))
    message[headers.SUBJECT] = "Test"
    message[headers.FROM] = "outside@example.com"
    message[headers.TO] = alias.address

    response = await handle(
        envelope=envelope,
        message=message,
    )

    new_statistics = client.get("/v1/server/statistics").json()

    assert previous_statistics["sent_emails_amount"] != new_statistics["sent_emails_amount"], \
        "sent emails amount should have changed"
    assert previous_statistics["trackers_removed_amount"] != \
           new_statistics["trackers_removed_amount"], "trackers removed amount should have changed"
    assert previous_statistics["proxied_images_amount"] == \
           new_statistics["proxied_images_amount"], "proxied images amount should not have changed"
    assert previous_statistics["users_amount"] != new_statistics["users_amount"],\
        "users amount should have changed"
    assert previous_statistics["aliases_amount"] != new_statistics["aliases_amount"], \
        "aliases amount should have changed"
    assert previous_statistics["app_version"] == constants.APP_VERSION, \
        "app version should not have changed"
