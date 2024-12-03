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

COPY . .

ENV UV_COMPILE_BYTECODE=1
RUN pip install uv
RUN make bootstrap

ENTRYPOINT ["bash"]
