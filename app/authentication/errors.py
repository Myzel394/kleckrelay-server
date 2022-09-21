class EmailLoginTokenExpiredError(Exception):
    pass


class EmailLoginTokenMaxTriesReachedError(Exception):
    pass


class EmailLoginTokenSameRequestTokenInvalidError(Exception):
    pass


class EmailIncorrectTokenError(Exception):
    pass
