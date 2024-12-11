FROM python:3.11

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

RUN pip install uv

COPY requirements_for_test.txt Makefile ./

ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR='/tmp/uv-cache/'
RUN uv venv
ENV PATH="/var/project/.venv/bin:$PATH"

RUN make bootstrap

COPY . .

ENTRYPOINT ["bash"]
