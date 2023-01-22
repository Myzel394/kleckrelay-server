FROM python:3.11-slim

ENV PYTHONPATH "/app"

# Install dependencies
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt install gunicorn3 gnupg2 postfix bsd-mailx -y \
    && pip install psycopg2

# Create gnupg path
RUN mkdir ~/.gnupg

RUN mkdir /app

WORKDIR /app

COPY pyproject.toml /app

# Install poetry
RUN pip3 install poetry

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Copy code
COPY . .
COPY server-entrypoint.sh .
COPY setup-postfix.sh .

EXPOSE 80 25 587

# Config Postfix
RUN chmod +x ./setup-postfix.sh

CMD ["./setup-postfix.sh"]
ENTRYPOINT ["/bin/bash", "./server-entrypoint.sh"]

