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

COPY . /app

WORKDIR /app

RUN make dependencies

ENV PATH $PATH:/app/.venv/bin
ENV PYTHONPATH $PYTHONPATH:/app/

ENTRYPOINT [ "bash" ]

EXPOSE 5000
CMD [ "/app/.venv/bin/python" "application/web.py" ]