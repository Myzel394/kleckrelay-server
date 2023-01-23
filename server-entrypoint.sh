echo "Starting KleckRelay API server" &&
poetry run alembic upgrade head &&
poetry run gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 app.main:app