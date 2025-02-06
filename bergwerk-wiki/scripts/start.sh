#!/bin/sh

sleep 5

if [ ! -f /tmp/first_run_done ]; then
    mediawiki-init.sh 
    touch /tmp/first_run_done
fi

service php8.3-fpm start 
service nginx start 

if [ ! -f /tmp/first_run_done ]; then
    python3 /usr/local/bin/load_data.py
fi

echo "Starting…"
exec "$@"