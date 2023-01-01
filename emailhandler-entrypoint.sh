#!/bin/bash

poetry run alembic upgrade head

poetry run python email_handler.py
