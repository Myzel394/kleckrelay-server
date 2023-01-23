#!/bin/bash

set -eu

echo "Configuring Postfix"

postconf -e "inet_protocols = ipv4"
postconf -e "maillog_file = /var/log/maillog"
postconf -e "mydestination = localhost"
postconf -e "mydomain = ${MAIL_DOMAIN}"
postconf -e "mynetworks = 127.0.0.0/8, [::1]/128"
postconf -e "myorigin = ${MAIL_DOMAIN}"
postconf -e "smtp_host_lookup = native,dns"
#postconf -e "smtp_sasl_auth_enable = yes"
#postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_password"
#postconf -e "smtp_sasl_security_options = noanonymous"
if [[ "${POSTFIX_USE_TLS,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  postconf -e "smtp_use_tls = yes"
fi
echo "nameserver 1.1.1.1" > /var/spool/postfix/etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf

echo "Creating broken symlinks"
cp -f /etc/services /var/spool/postfix/etc/services

echo "Postfix configuration completed"
echo "Starting Postfix"
postfix start
echo "Postfix started"
