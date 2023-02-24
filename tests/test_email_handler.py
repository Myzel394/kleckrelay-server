from email.message import EmailMessage

import pytest
from aiosmtpd.smtp import Envelope

from email_utils import status
from email_utils.bounce_messages import extract_forward_status, generate_forward_status, StatusType
from email_utils.handler import handle
from email_utils.utils import generate_message_id


@pytest.mark.asyncio
async def test_outside_can_send_to_local_user(
    create_user,
    create_random_alias,
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user)

    message = EmailMessage()
    envelope = Envelope()
    envelope.mail_from = "outside@example.com"
    envelope.rcpt_tos = [alias.address]

    response = await handle(
        envelope=envelope,
        message=message,
    )

    assert response == status.E200


@pytest.mark.asyncio
async def test_local_user_can_send_outside(
    create_user,
    create_random_alias,
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user)

    message = EmailMessage()
    envelope = Envelope()
    envelope.mail_from = user.email.address
    envelope.rcpt_tos = [f"outside_at_example.com_{alias.address}"]

    response = await handle(
        envelope=envelope,
        message=message,
    )

    assert response == status.E200


@pytest.mark.asyncio
async def test_local_user_can_not_send_from_other_alias(
    create_user,
    create_random_alias,
):
    user = create_user(is_verified=True)
    wrong_user = create_user(is_verified=True)
    alias = create_random_alias(user=user)

    message = EmailMessage()
    envelope = Envelope()
    envelope.mail_from = wrong_user.email.address
    envelope.rcpt_tos = [f"outside_at_example.com_{alias.address}",]

    response = await handle(
        envelope=envelope,
        message=message,
    )

    assert response == status.E502


@pytest.mark.asyncio
async def test_can_not_send_from_disabled_alias(
    create_user,
    create_random_alias,
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user, is_active=False)

    message = EmailMessage()
    envelope = Envelope()
    envelope.mail_from = user.email.address
    envelope.rcpt_tos = [f"outside_at_example.com_{alias.address}"]

    response = await handle(
        envelope=envelope,
        message=message,
    )

    assert response == status.E518


@pytest.mark.asyncio
async def test_outside_can_send_to_local_user_with_multipart(
    create_user,
    create_random_alias,
):
    user = create_user(is_verified=True)
    alias = create_random_alias(user=user)

    message = EmailMessage()
    envelope = Envelope()
    envelope.mail_from = "outside@example.com"
    envelope.rcpt_tos = [alias.address]

    message.set_content("Hello")
    message.add_alternative("<p>Hello</p>", subtype="html")

    response = await handle(
        envelope=envelope,
        message=message,
    )

    assert response == status.E200


def test_can_create_and_decrypt_forward_status_header():
    outside_address = "outside@kleckrelay.example"
    message_id = generate_message_id()

    header = generate_forward_status(
        status_type=StatusType.FORWARD_ALIAS_TO_OUTSIDE,
        outside_address=outside_address,
        message_id=message_id,
    )

    extracted = extract_forward_status(header)

    assert extracted["type"] == StatusType.FORWARD_ALIAS_TO_OUTSIDE.value
    assert extracted["outside_address"] == outside_address
    assert extracted["message_id"] == message_id
