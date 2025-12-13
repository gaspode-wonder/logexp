FROM python:3.10 AS base

COPY  . /opt/logexp/

WORKDIR /opt/logexp

RUN pip install -r docker-requirements.txt
ENV DATABASE_URL='postgresql://user:password@psql/logexp_dev'
RUN flask db init \
    && \
    flask db migrate -m "init" \
    && \
    flask db upgrade || true

EXPOSE 5000

CMD flask run


