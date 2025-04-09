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

# TODO: remove this once base python image no longer has issues with bdist_wheel https://github.com/docker-library/official-images/issues/18808
RUN pip install --upgrade pip setuptools

RUN make bootstrap

ENTRYPOINT ["bash"]
