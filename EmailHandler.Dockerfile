FROM python:3.11-slim

# Install dependencies
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt install gunicorn3 gnupg2 -y \
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
COPY emailhandler-entrypoint.sh .

# Run
EXPOSE 20381

ENTRYPOINT ["./emailhandler-entrypoint.sh"]
