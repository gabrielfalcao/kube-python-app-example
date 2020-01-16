from application.web import my_backend_function


def test_my_backend_function():
    ("web.my_backend_function should return a dictionary")

    # Given that I call my_backend_function
    result = my_backend_function()

    # When I check the result

    # Then it should be a dictionary
    result.should.be.a(dict)

    # And it should have one key: hello: world
    result.should.equal({"hello": "world"})
