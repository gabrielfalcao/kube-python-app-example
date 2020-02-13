from flaskhello.web import application
from sure import scenario


def before_each_test(context):
    context.web = application
    context.http = context.web.test_client()
    with context.http.session_transaction() as session:
        session["jwt_payload"] = {"user": {"name": "foo bar"}}


def after_each_test(context):
    # I would clean up the database here, if I had one
    pass


web_test = scenario(before_each_test, after_each_test)
