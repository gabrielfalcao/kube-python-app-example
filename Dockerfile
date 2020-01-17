FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    git


ENV VENV /venv/
ENV PATH "/venv/bin:${PATH}"

COPY . /app/

RUN /venv/bin/pip install /app
RUN /venv/bin/pip install uwsgi

RUN make tests

RUN flask-hello check
ENV FLASK_HELLO_PORT 5000

ENV FLASK_HELLO_VERSION 3

EXPOSE 5000

CMD flask-hello web --port=$FLASK_HELLO_PORT