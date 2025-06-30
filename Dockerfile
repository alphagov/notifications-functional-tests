FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /uvx /bin/

# Ensure we're using Chromium v126.x
# (Remove this if/when the performance regression in v127+ is resolved)
COPY ./debian.sources /etc/apt/sources.list.d/debian.sources

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        awscli \
        chromium \
        chromium-driver \
        jq \
        libzbar0 \
        poppler-utils \
        && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/project

COPY requirements_for_test.txt Makefile ./

ENV UV_CACHE_DIR='/tmp/uv-cache/'
ENV UV_COMPILE_BYTECODE=1
ENV VIRTUAL_ENV="/opt/venv"

RUN make bootstrap

COPY . .

ENTRYPOINT ["bash"]
