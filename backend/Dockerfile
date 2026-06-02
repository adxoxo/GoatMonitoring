# Backend image — Django + DRF served by Gunicorn (production).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# psycopg2-binary and pillow ship manylinux wheels, so no build toolchain
# is needed here — keeps the image small.
COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/production.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
