#!/bin/bash

echo "Configuring Postfix"

echo "Configuring basic Postfix config"
if [[ "${IS_DEBUG,,}" =~ ^(yes|true|t|1|y)$ ]]; then \
  echo "Debug mode is enabled, Postfix logs will be saved to /var/log/mail.log"
  postconf -e "maillog_file = /var/log/mail.log"
else
  echo "Debug mode is disabled, Postfix logs will not be saved"
  postconf -e "maillog_file = /dev/null"
fi

postconf -e "inet_protocols = ipv4"
postconf -e "inet_interfaces = all"
postconf -e "mydomain = ${MAIL_DOMAIN}"
postconf -e "mynetworks = 127.0.0.0/8, [::1]/128"
postconf -e "myorigin = ${MAIL_DOMAIN}"
postconf -e "myhostname = ${APP_DOMAIN}"
# Use Docker's built-in DNS server
postconf -e "resolve_numeric_domain = yes"
postconf -e "smtp_host_lookup = native,dns"
postconf -e "readme_directory = no"
#postconf -e "smtp_sasl_auth_enable = yes"
#postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_password"
#postconf -e "smtp_sasl_security_options = noanonymous"
echo "nameserver 1.1.1.1" > /var/spool/postfix/etc/resolv.conf
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

echo "Configuring DKIM for Postfix"
mkdir -p /etc/opendkim/keys

opendkim-genkey -r -h rsa-sha256 -s kleckrelay -d "${MAIL_DOMAIN}"
mkdir -p /etc/opendkim/keys/"${MAIL_DOMAIN}"
mv kleckrelay.private /etc/opendkim/keys/"${MAIL_DOMAIN}"/kleckrelay.private
mv kleckrelay.txt /tutorial/dns-for-dkim-txt-entry.txt

cat > /etc/opendkim/KeyTable<< EOF
kleckrelay._domainkey.${MAIL_DOMAIN} ${MAIL_DOMAIN}:kleckrelay:/etc/opendkim/keys/${MAIL_DOMAIN}/kleckrelay.private
EOF

cat > /etc/opendkim/SigningTable<< EOF
*@${MAIL_DOMAIN} kleckrelay._domainkey.${MAIL_DOMAIN}
EOF

cat > /etc/opendkim/TrustedHosts<< EOF
127.0.0.1
localhost
EOF

cat > /etc/opendkim.conf<< EOF
Canonicalization relaxed/relaxed
LogWhy Yes
Syslog Yes
SyslogSuccess Yes

ExternalIgnoreList refile:/etc/opendkim/TrustedHosts
InternalHosts refile:/etc/opendkim/TrustedHosts
KeyTable refile:/etc/opendkim/KeyTable
MinimumKeyBits 1024
Mode sv
PidFile /var/run/opendkim/opendkim.pid
SigningTable refile:/etc/opendkim/SigningTable
Socket inet:8891@127.0.0.1
TemporaryDirectory /var/tmp
UMask 022
UserID opendkim:opendkim

Domain ${MAIL_DOMAIN}
Selector kleckrelay
EOF
chown -R opendkim:opendkim /etc/opendkim
chmod go-rwx /etc/opendkim

postconf -e "smtpd_milters = inet:127.0.0.1:8891"
postconf -e "non_smtpd_milters = inet:127.0.0.1:8891"
postconf -e "milter_default_action = accept"
postconf -e "milter_protocol = 2"

cat >> /etc/default/opendkim<< EOF
SOCKET="inet:8891@localhost"
EOF

if [[ "${POSTFIX_USE_TLS,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  echo "Creating TLS certificate for Postfix"
  openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/private/ssl-cert-snakeoil.key -out /etc/ssl/certs/ssl-cert-snakeoil.pem -subj "/C=GB/ST=London/L=London/O=KleckRelay Instance/OU=${APP_DOMAIN}/CN=${MAIL_DOMAIN}"
  echo "Done creating TLS certificate."

  postconf -e "smtpd_tls_cert_file = /etc/ssl/certs/ssl-cert-snakeoil.pem"
  postconf -e "smtpd_tls_key_file = /etc/ssl/private/ssl-cert-snakeoil.key"
  postconf -e "smtp_tls_security_level = may"
  postconf -e "smtpd_tls_security_level = may"
fi

if [[ "${IS_DEBUG,,}" =~ ^(yes|true|t|1|y)$ ]]; then
  echo "Postfix will not be hardened as debug mode is enabled"
else
  echo "Hardening Postfix"
  postconf -e "smtpd_recipient_restrictions = reject_unauth_pipelining, reject_non_fqdn_recipient, reject_unknown_recipient_domain, permit_mynetworks, reject_unauth_destination, reject_rbl_client zen.spamhaus.org, reject_rbl_client bl.spamcop.net, check_policy_service unix:private/policyd-spf, permit"
  postconf -e "smtpd_sender_restrictions = permit_mynetworks, reject_non_fqdn_sender, reject_unknown_sender_domain, permit"
  postconf -e "smtpd_delay_reject = yes"
  postconf -e "smtpd_helo_required = yes"
  postconf -e "smtpd_helo_restrictions = permit_mynetworks, reject_non_fqdn_helo_hostname, reject_invalid_helo_hostname, permit"
fi

echo "Postfix configuration completed"
echo "Starting OpenDKIM"
service opendkim start
echo "Starting Postfix"
postfix start
echo "Postfix started"
