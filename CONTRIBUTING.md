## Email Handler

To test the email handler locally, make sure you have set the following
environment variables:

1. `IS_DEBUG=True`
2. `DEBUG_MAILS=True`

After that, you can send mails to the handler using `swaks`, here are some
example commands:

### Send a mail from outside mail to local mail

```commandline
swaks --to m1fNY7@mail.kleckrelay.com --from outside@example.com --server 127.0.0.1:20381 --header 'Subject: Hello'
```

### Send a mail with trackers in it

```commandline
swaks --to m1fNY7@mail.kleckrelay.com --from outside@example.com --server 127.0.0.1:20381 --header 'Subject: Hello'  --body explorative_tests/image_tracker_url.html 
```

See `explorative_tests` for more test files.
