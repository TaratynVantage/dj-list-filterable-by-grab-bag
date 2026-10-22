FROM ghcr.io/astral-sh/uv:latest AS uvlayer

FROM ubuntu:24.04 AS app

COPY --from=uvlayer /uv /uvx /usr/local/bin/

RUN mkdir -p /app/src
COPY pyproject.toml uv.lock .python-version /app/

WORKDIR /app
COPY src /app/src
WORKDIR /app/src
RUN /usr/local/bin/uv sync


ENTRYPOINT ["uv", "run", "runserver"]