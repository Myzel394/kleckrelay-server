# region 2** status
E200 = "250 Message accepted for delivery"
E201 = "250 KR E201"
E202 = "250 Unsubscribe request accepted"
E203 = "250 KR E203 email can't be sent from a reverse-alias"
E204 = "250 KR E204 ignore"
E205 = "250 KR E205 bounce handled"
# out-of-office status
E206 = "250 KR E206 Out of office"

# if mail_from is a IgnoreBounceSender, no need to send back a bounce report
E207 = "250 KR E207 No bounce report"

E208 = "250 KR E208 Hotmail complaint handled"

E209 = "250 KR E209 Email Loop"

E210 = "250 KR E210 Yahoo complaint handled"
E211 = "250 KR E211 Bounce Forward phase handled"
E212 = "250 KR E212 Bounce Reply phase handled"
E213 = "250 KR E213 Unknown email ignored"
E214 = "250 KR E214 Unauthorized for using reverse alias"
E215 = "250 KR E215 Handled dmarc policy"
E216 = "250 KR E216 Handled spf policy"

# endregion

# region 4** errors
# E401 = "421 KR E401 Retry later"
E402 = "421 KR E402 Encryption failed - Retry later"
# E403 = "421 KR E403 Retry later"
E404 = "421 KR E404 Unexpected error - Retry later"
E405 = "421 KR E405 Mailbox domain problem - Retry later"
E406 = "421 KR E406 Retry later"
E407 = "421 KR E407 Retry later"
E408 = "421 KR E408 Retry later"
E409 = "421 KR E409 Retry later"
E410 = "421 KR E410 Retry later"
# endregion

# region 5** errors
E501 = "550 KR E501"
E502 = "550 KR E502 Email not exist"
E503 = "550 KR E503"
E504 = "550 KR E504 Account disabled"
E505 = "550 KR E505"
E506 = "550 KR E506 Email detected as spam"
E507 = "550 KR E507 Wrongly formatted subject"
E508 = "550 KR E508 Email not exist"
E509 = "550 KR E509 unauthorized"
E510 = "550 KR E510 No such user"
E511 = "550 KR E511 unsubscribe error"
E512 = "550 KR E512 No such email log"
E514 = "550 KR E514 Email sent to noreply address"
E515 = "550 KR E515 Email not exist"
E516 = "550 KR E516 invalid mailbox"
E517 = "550 KR E517 unverified mailbox"
E518 = "550 KR E518 Disabled mailbox"
E519 = "550 KR E519 Email detected as spam"
E521 = "550 KR E521 Cannot reach mailbox"
E522 = (
    "550 KR E522 The user you are trying to contact is receiving mail "
    "at a rate that prevents additional messages from being delivered."
)
E523 = "550 KR E523 Unknown error"
E524 = "550 KR E524 Wrong use of reverse-alias"
# endregion
