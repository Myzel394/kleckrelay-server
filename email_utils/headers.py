MESSAGE_ID = "Message-ID"
IN_REPLY_TO = "In-Reply-To"
DATE = "Date"
SUBJECT = "Subject"
FROM = "From"
TO = "To"
CC = "Cc"
MIME_VERSION = "Mime-Version"
REPLY_TO = "Reply-To"
RECEIVED = "Received"
REFERENCES = "References"
CONTENT_TYPE = "Content-Type"
CONTENT_DISPOSITION = "Content-Disposition"
CONTENT_TRANSFER_ENCODING = "Content-Transfer-Encoding"
MIME_VERSION = "Mime-Version"
REPLY_TO = "Reply-To"
RECEIVED = "Received"
RSPAMD_QUEUE_ID = "X-Rspamd-Queue-Id"
SPAMD_RESULT = "X-Spamd-Result"
DKIM_SIGNATURE = "DKIM-Signature"
LIST_UNSUBSCRIBE = "List-Unsubscribe"
LIST_UNSUBSCRIBE_POST = "List-Unsubscribe-Post"
RETURN_PATH = "Return-Path"
X_SPAM_STATUS = "X-Spam-Status"

# headers used to DKIM sign in order of preference
DKIM_HEADERS = [
    [MESSAGE_ID.encode(), DATE.encode(), SUBJECT.encode(), FROM.encode(), TO.encode()],
    [FROM.encode(), TO.encode()],
    [MESSAGE_ID.encode(), DATE.encode()],
    [FROM.encode()],
]

MIME_HEADERS = [
    MIME_VERSION,
    CONTENT_TYPE,
    CONTENT_DISPOSITION,
    CONTENT_TRANSFER_ENCODING,
]
# convert to lowercase to facilitate header look up
MIME_HEADERS = [h.lower() for h in MIME_HEADERS]

AUTO_SUBMITTED = "Auto-Submitted"

# Yahoo complaint specific header
YAHOO_ORIGINAL_RECIPIENT = "original-rcpt-to"
