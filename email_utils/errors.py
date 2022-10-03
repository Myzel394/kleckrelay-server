class EmailHandlerError(Exception):
    pass


class InvalidEmailError(EmailHandlerError):
    pass


class NotYourAliasError(EmailHandlerError):
    pass
