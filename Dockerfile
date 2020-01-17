FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    build-base \
    bash \
    figlet

ENV PYTHONPATH /app/
ENV VENV /venv/

COPY . /app/

RUN make tests

ENV FLASK_HELLO_VERSION 1

EXPOSE 5000
CMD [ "/venv/bin/python" "application/web.py" ]