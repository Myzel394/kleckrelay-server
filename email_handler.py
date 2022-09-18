import time

from aiosmtpd.controller import Controller


class ExampleHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            ...
            print(f'> {ln}'.strip())
        print()
        print('End of message')
        return '250 Message accepted for delivery'


def main():
    controller = Controller(ExampleHandler(), hostname="0.0.0.0", port=20381)
    controller.start()

    while True:
        time.sleep(2)


if __name__ == "__main__":
    main()
