FROM python:3.4-slim

ENV PYTHONUNBUFFERED=1 \
	DEBIAN_FRONTEND=noninteractive \
	DISPLAY=:99.0

ADD mozilla.gpg /tmp/mozilla.gpg

RUN \
	echo "Install Debian packages" \
	&& echo "deb http://mozilla.debian.net/ jessie-backports firefox-release" >> /etc/apt/sources.list \
	&& apt-key add /tmp/mozilla.gpg \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		make \
		git \
		curl \
		build-essential \
		xvfb \
	&& apt-get install -y --no-install-recommends -t jessie-backports \
		firefox \

	&& echo "Clean up" \
	&& rm -rf /var/lib/apt/lists/* /tmp/*

RUN \
	echo "Install pip packages" \
	&& pip install \
		virtualenv

ADD xvfb/xvfb-init /etc/init.d/xvfb

WORKDIR /var/project
