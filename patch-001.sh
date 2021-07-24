#!/bin/bash
sudo rm -rf /opt/watchy/bond007-ui
wget https://github.com/benlycos/patch-watchy/raw/main/bond007-ui.tar.gz -O /tmp/bond007-ui.tar.gz
tar -xvf  /tmp/bond007-ui.tar.gz -C /opt/watchy/
sudo reboot
