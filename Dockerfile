FROM python:3.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR='/tmp/uv-cache/' \
    VIRTUAL_ENV="/opt/venv" \
    PATH="/opt/venv/bin:${PATH}"

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

RUN python -m venv /opt/venv && \
    make bootstrap

COPY . .

ENTRYPOINT ["bash"]
