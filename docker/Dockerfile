FROM python:3.4-slim

ARG APT_HTTP_PROXY

ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	DISPLAY=:99.0 \
	DBUS_SESSION_BUS_ADDRESS=/dev/null

ADD mozilla.gpg /tmp/mozilla.gpg
ADD chrome.pub /tmp/chrome.pub

RUN \
	echo "Install Debian packages" \
	&& ([ -z "$APT_HTTP_PROXY" ] || echo "Acquire::http::Proxy \"${APT_HTTP_PROXY}\";\n" > /etc/apt/apt.conf.d/99HttpProxy) \
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
		unzip \
		x11-utils \
	&& apt-get install -y --no-install-recommends -t jessie-backports \
		firefox-esr \
		google-chrome-stable \
	&& echo "Downloading latest chromedriver" \
	&& LATEST=$(curl -sSL http://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
	&& curl -sSLO http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip \
	&& unzip chromedriver_linux64.zip -d /opt/ \
	&& ln -fs /opt/chromedriver /usr/local/bin/chromedriver \
	&& rm chromedriver_linux64.zip \
	&& echo "Clean up" \
	&& rm -rf /var/lib/apt/lists/* /tmp/*

RUN \
	echo "Install pip packages" \
	&& pip install \
		virtualenv

ADD xvfb/xvfb-init /etc/init.d/xvfb

WORKDIR /var/project

COPY entrypoint.sh /usr/local/bin/docker-entrypoint

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
