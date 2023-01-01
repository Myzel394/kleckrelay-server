#!/bin/bash

poetry run alembic upgrade head

poetry run gunicorn -b 0.0.0.0:80 app.main:app