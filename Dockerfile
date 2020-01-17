FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    build-base \
    bash \
    figlet

ENV PYTHONPATH /app/
ENV VENV /venv/
ENV PATH /venv/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
COPY . /app/

RUN make tests

ENV FLASK_HELLO_VERSION 2

EXPOSE 5000

ENTRYPOINT [ "/venv/bin/python" ]
CMD [  "application/web.py" ]