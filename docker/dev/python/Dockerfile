FROM python:3.9

COPY ./app/requirements/ /opt/requirements/
RUN pip install -r /opt/requirements/dev.txt

COPY ./ /webserver

WORKDIR /webserver