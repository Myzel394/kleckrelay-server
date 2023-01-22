#!/bin/bash

set -eu

echo "Configuring Postfix"
postmap /etc/postfix/sasl_password

postconf -e "inet_protocols = ipv4"
postconf -e "maillog_file = /dev/null"
postconf -e "mydestination = localhost"
postconf -e "mydomain = ${MAIL_DOMAIN}"
postconf -e "mynetworks = 127.0.0.1/8"
postconf -e "myorigin = ${MAIL_DOMAIN}"
postconf -e "relayhost = [${MAIL_DOMAIN}]:${PORT:-587}"
postconf -e "smtp_host_lookup = native,dns"
#postconf -e "smtp_sasl_auth_enable = yes"
#postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_password"
#postconf -e "smtp_sasl_security_options = noanonymous"
if [[ "${POSTFIX_USE_TLS,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  postconf -e "smtp_use_tls = yes"
fi
echo "nameserver 1.1.1.1" > /var/spool/postfix/etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf

echo "Starting Postfix"
exec /usr/sbin/postfix start-fg