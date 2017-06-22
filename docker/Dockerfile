FROM python:3.4-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	DISPLAY=:99.0 \
	DBUS_SESSION_BUS_ADDRESS=/dev/null


RUN \
	echo "Install Debian packages" \
	&& ([ -z "$HTTP_PROXY" ] || echo "Acquire::http::Proxy \"${HTTP_PROXY}\";" > /etc/apt/apt.conf.d/99HttpProxy) \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		make \
		git \
		curl \
		build-essential \
		xvfb \
		unzip \
		x11-utils \
		nodejs \
		npm \
	&& ln -s /usr/bin/nodejs /usr/bin/node \
	&& npm -g install phantomjs-prebuilt

ADD mozilla.gpg /tmp/mozilla.gpg
RUN \
	echo "Installing firefox" \
	&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list \
	&& apt-key add /tmp/mozilla.gpg \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		firefox-esr

ADD chrome.pub /tmp/chrome.pub
RUN echo "Installing chromedriver" \
	&& apt-key add /tmp/chrome.pub \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		google-chrome-stable \
	&& LATEST=$(curl -x "$HTTP_PROXY" -sSL http://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
	&& curl -x "$HTTP_PROXY" -sSLO http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip \
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
