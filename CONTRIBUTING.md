# Contributing

To test KleckRelay locally, we strongly recommend to run the following services
as follows:

1. PostgreSQL -> Docker container
2. Main Worker -> On your machine
3. Email Handler -> On your machine

This setup makes it easier to debug the application as you will not need to rebuild
the whole docker images each time you change something.

Here's what to do based on what you want to contribute to

## Main Worker

To enable debug mode (which will allow logging as logs are disabled by default), edit the
following environmental variable:

1. `IS_DEBUG=true`

### Setting up the database

For the main Python worker you will need to run the database either by setting up
a manual PostgreSQL server or by running the `database` service inside the `docker-compose.yaml`
file.

The default database connection string should work out of the box using this setup, otherwise
edit the environmental variable `DB_URI`.

### Setting up emails

To receive emails locally, edit the following environmental variable:

1. `DEBUG_MAILS=true`

### Setting up a custom domain

To set up a custom domain, please see 
[how to set up a custom local domain](#how-to-set-up-a-custom-local-domain).


## Email Handler

**You only need to run the Email Handler when you want to change how 
incoming emails will be forwarded**

To enable debug mode (which will allow logging as logs are disabled by default), edit the
following environmental variable:

### Sending emails

To test the email handler locally, make sure you have set the following
environment variables:

1. `POSTFIX_HOST=127.0.0.1`
2. `POSTFIX_PORT=1025`
3. `POSTFIX_USE_TLS=False`

After that, you can send mails to the handler using `swaks`, here are some
example commands:

### Send a mail from outside mail to local mail

```commandline
swaks --to m1fNY7@mail.app.krl --from outside@example.com --server 127.0.0.1:20381 --header 'Subject: Hello'
```

### Send a mail with trackers in it

```commandline
swaks --to m1fNY7@mail.app.krl --from outside@example.com --server 127.0.0.1:20381 --header 'Subject: Hello'  --body explorative_tests/image_tracker_url.html 
```

See `explorative_tests` for more test files.


## How to set up a custom local domain

In order to access your localhost using a custom domain 
(for example `app.krl`) you can do the following.

When you set up a custom domain, make sure to change these environmental variables
(assuming you use `app.krl` and `mail.app.krl`):

```
APP_DOMAIN=app.krl
API_DOMAIN=app.krl
MAIL_DOMAIN=mail.app.krl
```

### Linux

1. Edit `/etc/hosts` (e.g. `vim /etc/hosts`)
2. Navigate to the line that starts with `127.0.0.1` (this will probably be one of the first lines)
3. Append your domains
   1. For KleckRelay we want to add `app.krl` to access the web interface and
   2. `mail.app.krl` for the emails.
4. Save the file
5. You can now access `localhost` using `app.krl`!
    1. Keep in mind that you need to prefix this domain with a protocol, as the browser otherwise will do a search query (e.g. instead of typing `app.krl`, type in `http://app.krl`)
6. To access the web interface in debug mode, go to  `http://app.krl:5173`
