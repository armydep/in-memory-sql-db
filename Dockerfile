FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY docker/memdb.toml /etc/memdb/memdb.toml

RUN python -m pip install --no-cache-dir . \
    && groupadd --gid 10001 memdb \
    && useradd --uid 10001 --gid memdb --create-home memdb \
    && install -d --owner=memdb --group=memdb /data

USER memdb

VOLUME ["/data"]

ENTRYPOINT ["memdb"]
CMD ["--config", "/etc/memdb/memdb.toml"]
