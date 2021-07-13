FROM joyzoursky/python-chromedriver:3.7-selenium

WORKDIR /var/project
COPY . .
RUN make bootstrap
ENTRYPOINT bash
