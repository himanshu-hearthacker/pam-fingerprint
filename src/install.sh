#!/bin/sh

find . -type f -name *.pyc -exec rm {} \;

cp etc/pamfingerprint.conf /etc/
## TODO
## chmod 600 /etc/pamfingerprint.conf

cp lib/security/pam_fingerprint.py /lib/security/
cp -r usr/lib/* /usr/lib/

cp var/log/pamfingerprint.log /var/log/
## TODO
chown 1000:1000 /var/log/pamfingerprint.log