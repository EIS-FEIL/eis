FROM python:3.12-slim

ENV LANG=C.utf8
RUN apt update
RUN apt install -y \
        pkg-config \
        libssl-dev \
        libcairo2-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        swig \
        gcc \
        tzdata
# swig gcc on m2crypto kompileerimiseks

RUN mkdir -p /srv/eis/install

WORKDIR /srv/eis

RUN python3 -m venv /srv/eis

COPY requirements.txt /srv/eis/install/requirements.txt
RUN /srv/eis/bin/pip install -r /srv/eis/install/requirements.txt

########################################################################
FROM python:3.12-slim
COPY --from=0 /srv/eis /srv/eis
COPY --from=0 /lib /lib

RUN echo "Europe/Tallinn" > /etc/timezone
RUN ln -fs /usr/share/zoneinfo/Europe/Tallinn /etc/localtime
ENV TZ="Europe/Tallinn"
ENV LANG=C.utf8

RUN apt update
RUN apt install -y \
        libmediainfo0v5 \
        vim-tiny procps wget curl net-tools tcpdump tcpflow
RUN /srv/eis/bin/pip install gunicorn

# Tõmba TARA identsustõendi avalik võti
RUN wget https://tara.ria.ee/oidc/jwks -O /srv/eis/etc/tara.jwks.json
RUN wget https://harid.ee/jwks.json -O /srv/eis/etc/harid.jwks.json

# Parandused
COPY formencode/FormEncode.?o /srv/eis/lib/python3.12/site-packages/formencode/i18n/et/LC_MESSAGES

COPY git-eiscore /srv/eis/git-eiscore
WORKDIR /srv/eis/git-eiscore
RUN /srv/eis/bin/pip install .

COPY . /srv/eis/git-eis
WORKDIR /srv/eis/git-eis
RUN bash install.sh

RUN chown -R www-data /srv/eis/var /srv/eis/lib/tmp /srv/eis/log

WORKDIR /srv/eis

RUN echo PYTHONPATH=$PYTHONPATH
EXPOSE 80
ENTRYPOINT ["/srv/eis/bin/gunicorn"]
CMD ["--paste", "/srv/eis/etc/config.ini", "-c", "/srv/eis/etc/gunicorn-conf.py", "-b", "0.0.0.0:80" ]
