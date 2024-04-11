FROM harbor.eenet.ee/eis/plank:0.0.19
RUN apt-get install -y cron docker.io
RUN apt-get autoremove -y
COPY ./crontab /etc/cron.d/eis-cron
RUN chmod 0644 /etc/cron.d/eis-cron
RUN crontab /etc/cron.d/eis-cron
ENTRYPOINT [ "cron", "-f" ]
