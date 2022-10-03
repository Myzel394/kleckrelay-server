class EmailHandlerError(Exception):
    pass


class InvalidEmailError(EmailHandlerError):
    pass


class AliasNotFoundError(EmailHandlerError):
    pass
