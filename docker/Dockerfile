FROM python:3.4-slim

ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	DISPLAY=:99.0

ADD mozilla.gpg /tmp/mozilla.gpg
ADD chrome.pub /tmp/chrome.pub

RUN \
	echo "Install Debian packages" \
	&& echo "deb http://mozilla.debian.net/ jessie-backports firefox-release" >> /etc/apt/sources.list \
	&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list \
	&& apt-key add /tmp/mozilla.gpg \
	&& apt-key add /tmp/chrome.pub \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		make \
		git \
		curl \
		build-essential \
		xvfb \
		wget \
		unzip \
	&& apt-get install -y --no-install-recommends -t jessie-backports \
		firefox \
		google-chrome-stable \
	&& echo "Downloading latest chromedriver" \
	&& LATEST=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
	&& wget http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip \
	&& unzip chromedriver_linux64.zip -d /usr/local/bin/ \
	&& rm chromedriver_linux64.zip \
	&& echo "Clean up" \
	&& rm -rf /var/lib/apt/lists/* /tmp/*

RUN \
	echo "Install pip packages" \
	&& pip install \
		virtualenv

ADD xvfb/xvfb-init /etc/init.d/xvfb

WORKDIR /var/project
