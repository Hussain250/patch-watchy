#!/bin/bash
rm -rf /opt/watchy/ 
wget https://github.com/benlycos/patch-watchy/raw/main/bond007-ui.tar.gz -O /tmp/bond007-ui.tar.gz
tar -xvf  /tmp/bond007-ui.tar.gz -C /opt/watchy/
