FROM python:3.11

WORKDIR /var/project

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        awscli \
        firefox-esr \
        jq \
        libzbar0 \
        poppler-utils \
        && \
    rm -rf /var/lib/apt/lists/*

RUN make bootstrap

ENTRYPOINT ["bash"]
