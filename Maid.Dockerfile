FROM python:3.11-slim

ENV PYTHONPATH "/app"

ARG DEBIAN_FRONTEND=noninteractive

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt install python3 python3-pip cron -y \
    && pip install psycopg2

RUN mkdir /app

WORKDIR /app

COPY pyproject.toml /app

# Install poetry
RUN pip3 install poetry

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Cron setup
COPY maid-jobs.txt /etc/cron.d/maid-jobs
RUN chmod 0644 /etc/cron.d/maid-jobs
RUN crontab /etc/cron.d/maid-jobs

RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
