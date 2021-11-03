FROM joyzoursky/python-chromedriver:3.9-selenium

WORKDIR /var/project
COPY . .
RUN make bootstrap
ENTRYPOINT bash
