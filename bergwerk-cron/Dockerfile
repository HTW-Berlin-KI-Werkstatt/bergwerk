FROM python:3.12

ENV BOT_USERNAME ${BOT_USERNAME}
ENV MEDIAWIKI_ADMIN_PASSWORD ${MEDIAWIKI_ADMIN_PASSWORD}

RUN apt-get update && apt-get install -y cron
COPY app /usr/src/app
COPY env.sh /usr/bin/env.sh
RUN chmod 755 /usr/bin/env.sh

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY crontab /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job
RUN crontab /etc/cron.d/my-cron-job
RUN touch /var/log/cron.log

ENTRYPOINT [ "/usr/bin/env.sh" ]
