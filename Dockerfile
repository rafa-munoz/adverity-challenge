FROM python:3.7

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements/base.txt requirements/base.txt
RUN pip install -r requirements/base.txt

ADD . /code

ENTRYPOINT ["scripts/docker-entrypoint.sh"]
