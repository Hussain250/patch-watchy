#!/bin/bash
sudo rm -rf /opt/watchy/bond007-ui
wget https://github.com/benlycos/patch-watchy/raw/main/bond007-ui.tar.gz -O /tmp/bond007-ui.tar.gz
tar -xvf  /tmp/bond007-ui.tar.gz -C /opt/watchy/
SRL_NO=$(cat /opt/watchy/bond007-id/serial.number)
SLACK_URL=$(wget -q https://raw.githubusercontent.com/benlycos/automation-tests/main/tests/slack_url.gpg -O - | openssl aes-256-cbc -d -a -pass pass:somepassword)
curl -X POST --data-urlencode "payload={\"text\": \"Patch patch-001 addition for ${SRL_NO} done. Device is going to get restarted\"}" ${SLACK_URL}
sudo reboot
