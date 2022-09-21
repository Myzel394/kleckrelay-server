# According to https://www.mailboxvalidator.com/resources/articles/acceptable-email-address-syntax-rfc/
LOCAL_REGEX = r"^[a-zA-Z0-9!\#\$\%\&\‘\*\+\–\/\=\?\^_\`\.\{\|\}\~.+-]{1,64}$"
DOMAIN_REGEX = r"^[a-zA-Z0-9-]{1,255}\.[a-zA-Z0-9-.]+$"
EMAIL_REGEX = f"^{LOCAL_REGEX[1:-1]}@{DOMAIN_REGEX[1:-1]}$"
PUBLIC_KEY_REGEX = r"-----BEGIN PUBLIC KEY-----(\n|\r|\r\n)([0-9a-zA-Z\+\/=]{64}(\n|\r|\r\n))*([0-9a-zA-Z\+\/=]{1,63}(\n|\r|\r\n))?-----END PUBLIC KEY-----"
PRIVATE_KEY_REGEX = r"-----BEGIN PRIVATE KEY-----(\n|\r|\r\n)([0-9a-zA-Z\+\/=]{64}(\n|\r|\r\n))*([0-9a-zA-Z\+\/=]{1,63}(\n|\r|\r\n))?-----END PRIVATE KEY-----"
