FROM gabrielfalcao/flask-hello-base

ENV PYTHONPATH /app/
ENV VENV /venv/

COPY . /app/

RUN make tests

ENV FLASK_HELLO_VERSION 1

ENTRYPOINT [ "bash" ]

EXPOSE 5000
CMD [ "/venv/bin/python" "application/web.py" ]