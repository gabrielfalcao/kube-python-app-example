FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    git

ENV PYTHONPATH="/app/:${PYTHONPATH}"
ENV VENV /venv/
ENV PATH="/venv/bin:${PATH}"

RUN /venv/bin/pip install coloredlogs ipdb

COPY . /app/

RUN make tests

ENV FLASK_HELLO_VERSION 3

EXPOSE 5000

ENTRYPOINT [ "/venv/bin/python" ]
CMD [  "application/web.py" ]