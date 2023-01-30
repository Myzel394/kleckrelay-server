#!/bin/bash

set -eu

echo "Configuring Postfix"

echo "Configuring basic Postfix config"
postconf -e "inet_protocols = ipv4"
postconf -e "inet_interfaces = all"
postconf -e "maillog_file = /var/log/maillog"
postconf -e "mydomain = ${MAIL_DOMAIN}"
postconf -e "mynetworks = 127.0.0.0/8, [::1]/128"
postconf -e "myorigin = ${MAIL_DOMAIN}"
postconf -e "myhostname = ${APP_DOMAIN}"
# Use Docker's built-in DNS server
postconf -e "resolve_numeric_domain = yes"
postconf -e "smtp_host_lookup = native,dns"
#postconf -e "smtp_sasl_auth_enable = yes"
#postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_password"
#postconf -e "smtp_sasl_security_options = noanonymous"
if [[ "${POSTFIX_USE_TLS,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  postconf -e "smtp_use_tls = yes"
fi
echo "nameserver 1.1.1.1" > /var/spool/postfix/etc/resolv.conf TODO: Check
echo "nameserver 1.1.1.1" > /etc/resolv.conf

echo "Creating broken symlinks for Postfix"
cp -f /etc/services /var/spool/postfix/etc/services

echo "Configuring incoming mail handling for Postfix"
cat > /etc/postfix/pgsql-relay-domains.cf<< EOF
hosts = $(echo "$DB_URI" | sed 's/.*@\([^/]*\).*/\1/')
user = $(echo "$DB_URI" | sed 's/postgresql:\/\///' | sed 's/@.*//' | cut -d':' -f1)
password = $(echo "$DB_URI" | sed 's/postgresql:\/\///' | sed 's/@.*//' | cut -d':' -f2)
dbname = $(echo "$DB_URI" | sed 's/.*\/\([^:]*\).*/\1/')

query = SELECT '%s' WHERE '%s' = '${MAIL_DOMAIN}' LIMIT 1;
EOF
cat > /etc/postfix/pgsql-transport-maps.cf<< EOF
hosts = $(echo "$DB_URI" | sed 's/.*@\([^/]*\).*/\1/')
user = $(echo "$DB_URI" | sed 's/postgresql:\/\///' | sed 's/@.*//' | cut -d':' -f1)
password = $(echo "$DB_URI" | sed 's/postgresql:\/\///' | sed 's/@.*//' | cut -d':' -f2)
dbname = $(echo "$DB_URI" | sed 's/.*\/\([^:]*\).*/\1/')

query = SELECT 'smtp:127.0.0.1:20381' WHERE '%s' = '${MAIL_DOMAIN}' LIMIT 1;
EOF
postconf -e "relay_domains = pgsql:/etc/postfix/pgsql-relay-domains.cf"
postconf -e "transport_maps = pgsql:/etc/postfix/pgsql-transport-maps.cf"

echo "Configuring SPF for Postfix"
cat >> /etc/postfix/master.cf<< EOF
policyd-spf  unix  -       n       n       -       0       spawn
    user=policyd-spf argv=/usr/bin/policyd-spf
EOF
postconf -e "policyd-spf_time_limit = 3600"


if [[ "${IS_DEBUG,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  postconf -e "smtp_use_tls = yes"
else
  echo "Hardening Postfix"
  postconf -e "smtpd_recipient_restrictions = reject_unauth_pipelining, reject_non_fqdn_recipient, reject_unknown_recipient_domain, permit_mynetworks, reject_unauth_destination, reject_rbl_client zen.spamhaus.org, reject_rbl_client bl.spamcop.net, check_policy_service unix:private/policyd-spf, permit"
  postconf -e "smtpd_sender_restrictions = permit_mynetworks, reject_non_fqdn_sender, reject_unknown_sender_domain, permit"
  postconf -e "smtpd_delay_reject = yes"
  postconf -e "smtpd_helo_required = yes"
  postconf -e "smtpd_helo_restrictions = permit_mynetworks, reject_non_fqdn_helo_hostname, reject_invalid_helo_hostname, permit"
fi

echo "Postfix configuration completed"
echo "Starting Postfix"
postfix start
echo "Postfix started"
