#!/bin/bash

set -eu

echo "Configuring Postfix"

echo "Configuring basic Postfix config"
postconf -e "inet_protocols = ipv4"
postconf -e "inet_interfaces = all"
postconf -e "maillog_file = /var/log/maillog"
postconf -e "mydestination = localhost, ${MAIL_DOMAIN}, localhost.${MAIL_DOMAIN}"
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


cat > /etc/postfix/virtual<< EOF
@${MAIL_DOMAIN}
EOF
postconf -e "virtual_alias_maps = hash:/etc/postfix/virtual"
postmap /etc/postfix/virtual

echo "Postfix configuration completed"
echo "Starting Postfix"
postfix start
echo "Postfix started"
