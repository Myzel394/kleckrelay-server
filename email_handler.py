import time
import traceback
from email import message_from_bytes
from mailbox import Message

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope

from app import life_constants, logger
from email_utils import status
from email_utils.bounce_messages import is_bounce, is_not_deliverable
from email_utils.errors import EmailHandlerError
from email_utils.handler import handle
from email_utils.sanitizers import sanitize_envelope, sanitize_message
from email_utils.send_mail import (
    draft_message, send_mail,
)


class ExampleHandler:
    def validate(self, envelope: Envelope) -> tuple[Envelope, Message]:
        logger.info("Validating data...")
        sanitize_envelope(envelope)

        logger.info("Sanitizing message...")
        message = message_from_bytes(envelope.original_content)
        sanitize_message(message)

        logger.info("Data validated successfully.")

        return envelope, message

    async def handle_DATA(self, server, session, envelope: Envelope):
        logger.info("New DATA received. Validating data...")

        message = None

        try:
            envelope, message = self.validate(envelope)

            logger.info(f"New mail received from {envelope.mail_from} to {envelope.rcpt_tos[0]}")

            if len(envelope.rcpt_tos) != 1 and not is_not_deliverable(envelope, message):
                send_mail(
                    to_mail=envelope.mail_from,
                    message=draft_message(
                        template="not-deliverable-to-server",
                        subject="Your email could not be delivered",
                        context={
                            "title": "Your email is not compatible with our server.",
                            "preview_text": "We could not deliver your email.",
                            "body":
                                f"We are sorry, but we couldn't deliver your email to your "
                                f"destination. You tried sending an email to "
                                f"{len(envelope.rcpt_tos)} recipients, but we currently only "
                                f"support sending it to one recipient at a time."
                            ,
                            "explanation":
                                "We can't deliver your email to multiple recipients at the same "
                                "time, but you can send the same email multiple times to one "
                                "recipient at a time. ",
                            "server_url": life_constants.APP_DOMAIN,
                        }
                    )
                )
                return status.E501

            status_code = await handle(envelope, message)

            logger.info(f"Mail handled successfully. Returning status code: {status_code}.")

            return status_code

        except EmailHandlerError as error:
            logger.info("An EmailHandlerError occurred while handling the mail.")

            if not error.avoid_error_email and not is_not_deliverable(envelope, message):
                send_mail(
                    to_mail=envelope.mail_from,
                    message=draft_message(
                        template="not-deliverable-to-server",
                        subject="Your email could not be delivered",
                        context={
                            "title": "We could not deliver your email.",
                            "preview_text": "We could not deliver your email.",
                            "body":
                                f"We are sorry, but we couldn't deliver your email to "
                                f"{envelope.rcpt_tos[0]}. An error occurred while processing your "
                                f"email. The given error was: {error}"
                            ,
                            "explanation": "We recommend you to try again later.",
                            "server_url": life_constants.APP_DOMAIN,
                        }
                    )
                )

            return status.E200

        except Exception as error:
            logger.warning("An error occurred while handling the mail.")
            traceback.print_exception(error)
            logger.info(
                f"Error occurred while handling mail from {envelope.mail_from} to "
                f"{envelope.rcpt_tos}."
            )

            return status.E501


def main():
    controller = Controller(
        ExampleHandler(),
        hostname=life_constants.EMAIL_HANDLER_HOST,
        port=20381
    )
    controller.start()

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()
