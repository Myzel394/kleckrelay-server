import time
import traceback
from email import message_from_bytes
from mailbox import Message

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope

from app import logger
from email_utils import status
from email_utils.handler import handle
from email_utils.sanitizers import sanitize_envelope, sanitize_message
from email_utils.send_mail import (
    send_error_mail,
)


class ExampleHandler:
    def validate(self, envelope: Envelope) -> tuple[Envelope, Message]:
        sanitize_envelope(envelope)

        message = message_from_bytes(envelope.original_content)
        sanitize_message(message)

        logger.info("Data validated successfully.")

        return envelope, message

    async def handle_DATA(self, server, session, envelope: Envelope):
        logger.info("New DATA received. Validating data...")

        try:
            envelope, message = self.validate(envelope)

            logger.info(f"New mail received from {envelope.mail_from} to {envelope.rcpt_tos[0]}")

            return handle(envelope, message)
        except Exception as error:
            traceback.print_exception(error)

            send_error_mail(
                mail=envelope.mail_from,
                targeted_mail=envelope.rcpt_tos[0],
            )

            return status.E501


def main():
    controller = Controller(ExampleHandler(), hostname="0.0.0.0", port=20381)
    controller.start()

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()
