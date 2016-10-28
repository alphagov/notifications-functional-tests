#!/bin/bash

# remove any previous screenshots
if [ -d screenshots ]; then
  echo 'Removing old test screenshots'
  rm -rfv screenshots
fi
mkdir screenshots

# remove any previous browser log
rm -f chromedriver.log
