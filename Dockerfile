FROM python:3.10 AS base

COPY . /opt/logexp/

WORKDIR /opt/logexp

RUN pip install -r docker-requirements.txt
ENV DATABASE_URL='postgresql://jebbaugh@localhost:5432/Experiments'
RUN flask db init \
    && \
    flask db migrate -m "init" \
    && \
    flask db upgrade || true

CMD flask run --host 0.0.0.0


