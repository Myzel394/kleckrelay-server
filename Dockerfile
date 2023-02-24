FROM python:3.11-slim

ENV PYTHONPATH "/app"

EXPOSE 80 25 587

# Install dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN echo "postfix postfix/mailname string ${MAIL_DOMAIN}" | debconf-set-selections && \
    echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt install python3 python3-pip gunicorn3 gnupg2 postfix postfix-pgsql postfix-policyd-spf-python opendkim opendkim-tools dnsutils -y \
    && pip install psycopg2

# Create gnupg path
RUN mkdir ~/.gnupg

RUN mkdir /app
RUN mkdir /tutorial

# Install poetry
RUN pip3 install poetry

WORKDIR /app
COPY pyproject.toml /app

# Install dependencies
# Installind `cython` manually is required for talon
RUN poetry install cython --no-interaction --no-ansi
RUN poetry install --only main --no-interaction --no-ansi

# Copy code
COPY . .
COPY server-entrypoint.sh .
COPY setup-postfix.sh .
COPY maid.py .
COPY maid-jobs.txt .
COPY email_handler.py .

# Force key generation on first run
RUN rm /etc/ssl/certs/ssl-cert-snakeoil.pem

# Config Postfix
RUN chmod +x ./setup-postfix.sh

ENTRYPOINT ["sh", "-c", "./setup-postfix.sh && ./server-entrypoint.sh"]
