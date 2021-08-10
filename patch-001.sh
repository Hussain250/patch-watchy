#!/bin/bash
sudo rm -rf /opt/watchy/bond007-ui
TEMP_DIR=$(mktemp /tmp/watchy-patch-XXXXXX)
wget -N "https://github.com/benlycos/patch-watchy/raw/main/bond007-ui.tar.gz" -P "${TEMP_DIR}/"
sudo tar -xf  "${TEMP_DIR}/bond007-ui.tar.gz" -C "/opt/watchy/"
sudo wget -N "https://github.com/benlycos/patch-watchy/raw/main/maxwell.cfg" -P "/opt/watchy/bond007-core/conf/"
SRL_NO=$(cat /opt/watchy/bond007-id/serial.number)
SLACK_URL=$(wget -q https://raw.githubusercontent.com/benlycos/automation-tests/main/tests/slack_url.gpg -O - | openssl aes-256-cbc -d -a -pass pass:somepassword)
curl -X POST --data-urlencode "payload={\"text\": \"Patch patch-001 addition for ${SRL_NO} done. Device is going to get restarted\"}" ${SLACK_URL}
sudo reboot
