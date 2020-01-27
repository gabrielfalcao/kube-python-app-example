FROM gabrielfalcao/flask-hello-base

RUN apk --update --no-cache add \
    git


ENV VENV /venv/
ENV PATH "/venv/bin:${PATH}"
ENV PYTHONPATH /app/

COPY . /app/

RUN /venv/bin/pip install /app
RUN /venv/bin/pip install uwsgi

RUN make tests

ENV OAUTH2_DOMAIN           dev-newstore.auth0.com
ENV OAUTH2_CALLBACK_URL     https://newstoresauth0ldap.ngrok.io/callback/auth0
ENV OAUTH2_CLIENT_ID        FROM_DOCKERFILE_PLEASE_OVERRIDE
ENV OAUTH2_CLIENT_SECRET    FROM_DOCKERFILE_PLEASE_OVERRIDE
ENV OAUTH2_BASE_URL         https://dev-newstore.auth0.com
ENV OAUTH2_ACCESS_TOKEN_URL https://dev-newstore.auth0.com/oauth/token
ENV OAUTH2_AUTHORIZE_URL    https://dev-newstore.auth0.com/authorize
ENV OAUTH2_CLIENT_SCOPE     openid profile email

RUN flask-hello check
ENV FLASK_HELLO_PORT 5000

ENV FLASK_HELLO_VERSION 3

EXPOSE 5000
EXPOSE 4242
EXPOSE 6969

CMD flask-hello web "--port=$FLASK_HELLO_PORT"
CMD /venv/bin/uwsgi --http ":$FLASK_HELLO_PORT" --mount /=application.web:application
