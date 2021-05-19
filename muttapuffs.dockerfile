FROM python:3 

RUN pip install numpy

WORKDIR /golem/work
VOLUME /golem/work /golem/output /golem/resource