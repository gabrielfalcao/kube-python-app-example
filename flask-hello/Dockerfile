FROM python:3.7-alpine

RUN apk --update --no-cache add \
    build-base \
    ca-certificates \
    make \
    python3-dev

ENV PATH $PATH:/app/.venv/bin
ENV PYTHONPATH $PYTHONPATH:/app/

COPY . /app

WORKDIR /app

RUN make tests

ENTRYPOINT [ "/app/.venv/bin/python" ]

CMD [ "application/web.py" ]