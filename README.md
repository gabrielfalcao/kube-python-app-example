# NewStore Cloud Developer Task

## Introduction

This is a two-step code challenge with the following **GOAL**:

    Deliver a small and simple flask-based RESTful-ish API for managing users

#### Part 1

- The candidate should extend the existing code to implement at least one of the user stories below.


#### Part 2

The candidate comes for an in-house interview (or remote interview)
where they will pair-program with a NewStore engineer to further extend the code.



## Guiding Principles

* The application server should be working.
* Show how you would write unit and/or functional tests for your application.
* Store data however you want: a json file, csv, sqlite, mysql or whatever you want. As long as the tests are passing and you have a functional application.
* Deliver as many of the user stories below as possible. But do not
  worry about getting all of them done. The focus here is to see your
  workflow.
* **Preferably** write your tests before writing application code, you will be asked about your thought process.
* You **must** deliver a functional test suite to prove that your RESTful API works. (look at existing functional tests for examples)


## Setting up your environment

You will need:

- Python 3.6 or superior
- [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
- Operating system: Linux or MacOSX (no support for windows)

This challenge code is a basic [flask](https://flask.palletsprojects.com/en/1.1.x/) web application.

### Setup commands

All the commands below assume you have
[make](https://www.gnu.org/software/make/) installed, it comes
installed in MacOS and can be installed in ubuntu with `sudo apt
install make`. If you use a different linux distribution please make
sure to install it.

The purpose of `make` is to automate the maintenance and testing of
the code, we use it every day at *NewStore* so if you're not familiar
with it this is a good chance to get acquainted.

(Feel free to open the file `Makefile` in your editor to see what it is doing)

#### Ensure dependencies

Create virtualenv and install dependencies with:

```bash
make dependencies
```

This will:

1. Create a python3 virtualenv under `.venv`
2. Install the latest pip in the virtualenv
3. Install all dependencies from `development.txt`


#### Tests

This project comes with unit and functional tests to provide you with
the [fastest feedback
loop](https://blog.bitsrc.io/a-guide-to-test-driven-development-tdd-shorter-feedback-loop-faster-workflow-ce5bd6b247c4).

You can find existing examples [test functions](https://nose.readthedocs.io/en/latest/writing_tests.html#test-functions) for unit tests under
`tests/unit/test_*.py` and functional tests under
`tests/functional/test_*.py`.

- Unit tests cannot perform I/O, instead they should mock things.
- Functional tests are allowed to perform real I/O (such as database calls, or writing files to disk), but should clean up after themselves.

##### Running tests

Run unit tests with

```bash
make unit
```

And functional tests with

```bash
make functional
```

**Reference/Documentation to help you**

* Under the hood `make tests` will use [nose](https://nose.readthedocs.io/en/latest/writing_tests.html#test-functions) as test runner.
* Write your assertions using [sure](https://sure.readthedocs.io/en/latest/api-reference.html#setup-teardown)

* You can generate hashes using the [hashlib](https://docs.python.org/3.6/library/hashlib.html)

* If you decide to use a SQL database, you might want to use [SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/)


##### Running the server

```bash
make run
```

## Ready to start ?

Here are the [user stories](http://martinfowler.com/bliki/GivenWhenThen.html) that
you need to deliver.

Imagine that you are already working at NewStore and each story is a
ticket that you are closing in a normal day of work.

Also keep in mind you are writing code that will need to be maintained
by other people, so
[quality](https://en.wikipedia.org/wiki/Software_craftsmanship#Manifesto)
matters over quantity.



### Story 1: Create a simple endpoint that generates an md5 hash of an arbitrary email

```gherkin
Given the arbitrary email address "user@newstore.com"
When I POST a json payload with '{"data": "user@newstore.com"}' to the URL "/api/calculate-md5"
Then it should return a json that looks like this: '{"md5": "8c3a7ee05457d337d5bb14f438464cbf"}'
```

### Story 2: Build API endpoint that allows user creation

```gherkin
Given a JSON payload containing the fields:
  | field      | value            |
  | first_name | Guido            |
  | email      | guido@python.org |
  | password   | py123            |
When I POST on "/api/user"
Then it should store the user and return a JSON response with the fields:
  {
    "first_name": "Guido",
    "uuid": "02fd0bf3d9518a801517fd6fac005878",
    "email": "guido@python.org"
  }
And it should be stored in some sort of database
```

    Notes:
      1. Generate the UUID with the pseudo-algorithm:
         uuid = md5digest("newstore:guido@python.org")

      2. Store password securely.

### Story 3: Build API endpoint for editing users

```gherkin
Given that the following users exist in the databse:
  | first_name | email            | password  |
  | Guido      | guido@python.org | py123     |
When I PUT on "/api/user/02fd0bf3d9518a801517fd6fac005878" with the a JSON payload containing:
  {
    "password": "anotherpw"
  }
Then the database should have the users:
  | first_name | email            | password   |
  | Guido      | guido@python.org | anotherpw  |
And it should return a JSON response with the fields:
  {
    "first_name": "Guido",
    "uuid": "02fd0bf3d9518a801517fd6fac005878",
    "email": "guido@python.org"
  }
```

### Story 4: Build API endpoint for retrieving a user

```gherkin
Given that the following users exist in the databse:
  | first_name | email            |
  | Guido      | guido@python.org |
When I GET on "/api/user/02fd0bf3d9518a801517fd6fac005878"
Then it should return a JSON response with the user data
  {
    "first_name": "Guido",
    "uuid": "02fd0bf3d9518a801517fd6fac005878",
    "email": "guido@python.org"
  }
```

### Story 5: Build API endpoint for retrieving a list of users

```gherkin
Given that the following users exist in the databse:
  | first_name | email            |
  | Guido      | guido@python.org |
  | Foo        | foo@bar.com      |

When I GET on "/api/users"
Then it should return a JSON response with a list of the existing users
```

### Story 6: Build API endpoint for removing users

```gherkin
Given that the following users exist in the databse:
  | first_name | email            | password  |
  | Guido      | guido@python.org | py123     |
  | Foo        | foo@bar.com      | foobar123 |
When I DELETE on "/api/user/guido@python.org"
Then it should return the deleted user info in the response
And now the database should only contain the users:
  | first_name | email            | password  |
  | Foo        | foo@bar.com      | foobar123 |
```

## Happy Hacking and good luck!
