FROM python:3.7-alpine

RUN apk --update --no-cache add \
    build-base \
    ca-certificates \
    libffi-dev \
    make \
    gcc \
    musl-dev \
    postgresql-libs \
    postgresql-dev \
    python3-dev

ENV PATH $PATH:/app/.venv/bin
ENV PYTHONPATH $PYTHONPATH:/app/

COPY . /app

WORKDIR /app

RUN make dependencies

ENV FLASK_HELLO_VERSION 1

ENTRYPOINT [ "bash" ]

EXPOSE 5000
CMD [ "/app/.venv/bin/python" "application/web.py" ]