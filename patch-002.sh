#!/bin/bash
mkdir -p /opt/watchy/bond007-patches/

TEMP_DIR=$(mktemp -d -t watchy-XXXXXXXXXX)
SRL_NO=$(cat /opt/watchy/bond007-id/serial.number)
SLACK_URL=$(wget -q https://raw.githubusercontent.com/benlycos/automation-tests/main/tests/slack_url.gpg -O - | openssl aes-256-cbc -d -a -pass pass:somepassword)

if [ -e /opt/watchy/bond007-patches/patch-002 ]
then
    curl -X POST --data-urlencode "payload={\"text\": \"Patch patch-001 already exits for ${SRL_NO}. No patch-001 required\"}" ${SLACK_URL} >> "${TEMP_DIR}/run.log"
    rm -rf ${TEMP_DIR}
elif [ -e /opt/watchy/bond007-patches/patch-001 ]
then
    sudo rm /opt/watchy/bond007-ui/render.py
    wget -qcN "https://raw.githubusercontent.com/benlycos/patch-watchy/main/patch-002/render.py" -O "/opt/watchy/bond007-ui/render.py" > "${TEMP_DIR}/run.log"
    wget -qcN "https://raw.githubusercontent.com/benlycos/patch-watchy/main/patch-002/net_speed.py" -O "/opt/watchy/bond007-ui/net_speed.py" >> "${TEMP_DIR}/run.log"
    sudo rm /opt/watchy/bond007-ui/templates/dial_page.html
    wget -qcN "https://raw.githubusercontent.com/benlycos/patch-watchy/main/patch-002/dial_page.html" -O "/opt/watchy/bond007-ui/templates/dial_page.html" >> "${TEMP_DIR}/run.log"
    curl -X POST --data-urlencode "payload={\"text\": \"Patch patch-002 addition for ${SRL_NO} done. Device is going to get restarted\"}" ${SLACK_URL} >> "${TEMP_DIR}/run.log"
    rm -rf ${TEMP_DIR}
    touch /opt/watchy/bond007-patches/patch-002
    sudo reboot
else
    curl -X POST --data-urlencode "payload={\"text\": \"Add patch-001 before adding patch-002 for ${SRL_NO}. patch-001 required\"}" ${SLACK_URL} >> "${TEMP_DIR}/run.log"
fi
