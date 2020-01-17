FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    git

ENV VENV /venv/
ENV PATH="/venv/bin:${PATH}"

COPY . /app/

RUN make tests

ENV FLASK_HELLO_VERSION 3

EXPOSE 5000
