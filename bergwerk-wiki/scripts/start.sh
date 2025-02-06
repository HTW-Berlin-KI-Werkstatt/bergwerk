#!/bin/sh

sleep 5

if [ ! -f /tmp/first_run_done ]; then
    mediawiki-init.sh 
fi

service php8.3-fpm start 
service nginx start 

if [ ! -f /tmp/first_run_done ]; then
    python3 /usr/local/bin/load_data.py
    touch /tmp/first_run_done
fi

echo "Starting…"
exec "$@"