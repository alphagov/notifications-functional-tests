#!/usr/bin/env bash

set -eo pipefail

USER_EXISTS=$(id -u testuser > /dev/null 2>&1; echo $?)
GROUP_EXISTS=$(cat /etc/group | grep ":$GID:" | wc -l)


# User exists
if [ $USER_EXISTS -eq 0 ]; then
    echo 'User exists'
# User doesn't exist, create testuser
else
    useradd -ms /bin/bash testuser
fi

# Group doesn't exist, create group and user
if [ $GROUP_EXISTS == "0" ]; then
    groupadd -g $GID testuser
    usermod -a -G testuser testuser

# Group exists, add user
else
    GROUP_NAME=$(getent group $GID | cut -d: -f1)
    usermod -a -G $GROUP_NAME testuser
fi

exec "$@"
