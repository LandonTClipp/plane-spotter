FROM python:3.10-alpine

WORKDIR /usr/app/src
COPY .. /usr/app/src

RUN apk upgrade && apk add chromium chromium-chromedriver
RUN python3 -m venv ve &&  \
    source ve/bin/activate &&  \
    pip install -Ue .[dev]

COPY ./docker/docker-entrypoint.sh /usr/bin/docker-entrypoint
RUN chmod +x /usr/bin/docker-entrypoint

VOLUME /usr/app/src/production_config

ENTRYPOINT ["docker-entrypoint"]
