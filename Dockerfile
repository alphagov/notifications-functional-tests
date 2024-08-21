# The jorzoursky/python-chromedriver image does not have a published 3.11 tag yet, so copy the dockerfile across from
# https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py-debian/3.11-selenium/Dockerfile
FROM python:3.11 as python-chromedriver-copy

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
####
# Fix version of google-chrome-stable to avoid breaking changes.
# Breaking changes were in version 127.0.6533.88
# RUN apt-get install -y google-chrome-stable
RUN cd /tmp && \
    wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_126.0.6478.126-1_amd64.deb && \
    apt install -y ./google-chrome-stable_126.0.6478.126-1_amd64.deb && \
    rm google-chrome-stable_126.0.6478.126-1_amd64.deb
####

# install chromedriver
RUN apt-get install -yqq unzip jq
####
# Fix version of chromedriver to avoid breaking changes. See above.
# RUN curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -rc '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64").url' > /tmp/chromedriver_url
# RUN wget -O /tmp/chromedriver.zip `cat /tmp/chromedriver_url`
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip
#
####
RUN unzip -j /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install selenium

# --------------- Our own dockerfile instructions follow:

FROM python-chromedriver-copy AS functional-tests-image

RUN apt install -y awscli poppler-utils libzbar0

WORKDIR /var/project
COPY . .
RUN make bootstrap
ENTRYPOINT bash
