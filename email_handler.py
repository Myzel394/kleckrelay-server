import time

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope

from app import logger
from app.database.dependencies import with_db
from app.main import app as mail_app
from app.models import Email
from email_utils.send_mail import send_mail
from email_utils.utils import parse_destination_email, sanitize_email


class ExampleHandler:
    async def handle_DATA(self, server, session, envelope: Envelope):
        logger.info(f"New mail received from {envelope.mail_from}")

        try:
            with with_db() as db:
                logger.info(f"Retrieving mail {envelope.mail_from} from database")
                email = db.query(Email).filter(Email.address == envelope.mail_from).first()

                if email:
                    logger.info(
                        f"Email {envelope.mail_from} is a locally saved user. Relaying email to "
                        f"destination."
                    )
                    # Forward email FROM private mail TO destination
                    local_alias, forward_address = parse_destination_email(
                        user=email.user,
                        email=envelope.rcpt_tos[0],
                    )
                    logger.info(
                        f"Email {envelope.mail_from} should be relayed to {forward_address}. "
                        f"Sending email now..."
                    )

                    send_mail(
                        to_mail=forward_address,
                        from_mail=local_alias,
                        plaintext=envelope.original_content,
                        subject="Test",
                    )

                print(email)
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
