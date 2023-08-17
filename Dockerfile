FROM joyzoursky/python-chromedriver:3.9-selenium

RUN apt install -y poppler-utils libzbar0

WORKDIR /var/project
COPY . .
RUN make bootstrap
ENTRYPOINT bash
