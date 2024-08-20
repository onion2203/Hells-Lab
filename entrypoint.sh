#!/bin/sh

mv /flag.txt /flag$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 20).txt

chmod 644 /flag*.txt
chattr +i /flag*.txt
chmod 600 /entrypoint.sh

/usr/bin/supervisord -c /etc/supervisord.conf