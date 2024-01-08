# The jorzoursky/python-chromedriver image does not have a published 3.11 tag yet, so copy the dockerfile across from
# https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py-debian/3.11-selenium/Dockerfile
FROM python:3.11 as python-chromedriver-copy

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install selenium

# --------------- Our own dockerfile instructions follow:

FROM python-chromedriver-copy AS functional-tests-image

RUN apt install -y poppler-utils libzbar0

WORKDIR /var/project
COPY . .
RUN make bootstrap
ENTRYPOINT bash
