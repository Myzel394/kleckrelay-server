import time

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope

from app import logger
from app.database.dependencies import with_db
from email_utils.send_mail import (
    send_mail_from_outside_to_private_mail,
    send_mail_from_private_mail_to_destination,
)
from email_utils.utils import get_alias_email, get_local_email, validate_email


class ExampleHandler:
    def handle(self, envelope: Envelope):
        logger.info("Retrieving mail from database.")

        with with_db() as db:
            logger.info(f"Checking if FROM mail {envelope.mail_from} is locally saved.")

            if email := get_local_email(db, email=envelope.mail_from):
                # LOCALLY saved user wants to send a mail FROM its private mail TO the outside.
                logger.info(
                    f"Email {envelope.mail_from} is a locally saved user. Relaying email to "
                    f"destination {envelope.rcpt_tos[0]}."
                )
                send_mail_from_private_mail_to_destination(envelope, email)
                return

            logger.info(
                f"Checking if DESTINATION mail {envelope.rcpt_tos[0]} is an alias mail."
            )

            if alias := get_alias_email(db, email=envelope.rcpt_tos[0]):
                # OUTSIDE user wants to send a mail TO a locally saved user's private mail.
                logger.info(
                    f"Email {envelope.mail_from} is from outside and wants to send to alias "
                    f"{alias.address}. "
                    f"Relaying email to locally saved user {alias.user.email.address}."
                )
                send_mail_from_outside_to_private_mail(envelope, alias)

    async def handle_DATA(self, server, session, envelope: Envelope):
        logger.info("New DATA received. Validating data...")

        try:
            validate_email(envelope.mail_from)

            for mail in envelope.rcpt_tos:
                validate_email(mail)

            logger.info("Data validated successfully.")

            logger.info(f"New mail received from {envelope.mail_from} to {envelope.rcpt_tos[0]}")

            self.handle(envelope)
        except Exception as error:
            print("blaa")
            print(error)
        """
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            ...
            print(f'> {ln}'.strip())
        print()
        print('End of message')"""

        return '250 Message accepted for delivery'


def main():
    controller = Controller(ExampleHandler(), hostname="0.0.0.0", port=20381)
    controller.start()

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()
