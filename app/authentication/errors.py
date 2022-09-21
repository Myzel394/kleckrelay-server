class EmailLoginTokenExpiredError(Exception):
    pass


class EmailLoginTokenMaxTriesReachedError(Exception):
    pass


class EmailLoginTokenSameRequestTokenInvalidError(Exception):
    pass
