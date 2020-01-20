------

Python Application in Kubernetes Stack
======================================

What is
-------

- Flask Web API
- ZeroMQ Client (REQ)
- ZeroMQ Worker (REP)
- ZeroMQ Queue (ROUTER + DEALER)
- ZeroMQ Forwarder (PUB/SUB)
- PostgreSQL
- Redis

Deployment
----------

Helm chart deploys all dependencies to a Kubernetes namespace.

`operations/helm`_

Developing
----------

1. Install all dependencies and run tests

.. code:: bash

   make tests

2. Create postgresql database and user

.. code:: bash

   make db


3. Run web app

.. code:: bash

   make run
