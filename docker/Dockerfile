FROM python:3.5-slim-buster

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
		gnupg

ADD mozilla.gpg /tmp/mozilla.gpg
RUN \
	echo "Installing firefox" \
	&& apt-key add /tmp/mozilla.gpg \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		firefox-esr

RUN \
	echo "Install pip packages" \
	&& pip install \
		virtualenv

ADD xvfb/xvfb-init /etc/init.d/xvfb

WORKDIR /var/project

COPY entrypoint.sh /usr/local/bin/docker-entrypoint

ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
