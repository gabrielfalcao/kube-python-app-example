------

Kubernetes Sandbox
==================



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




Deploying
---------


.. code:: bash

   helm install --atomic operations/helm
