------

Python Application deployed Kubernetes Stack
============================================

1. Simple Flask app
2. Automated deployment with Toolbelt + K8S + Helm
3. Runs tunneled with ngrok both locally and on K8S making testing easy and seamless




Running locally
---------------

    NOTE: You need to have postgres running locally



1. (Re)create database and user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: bash

   make db



2. Run web server on port 5000
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: bash

   make run


3. Run tunnel on another port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: bash

   make tunnel



Deploying
---------



NOTES:

- You need to have Toolbelt installed and configured locally

- If you have any local commits please push to github to build the
  latest docker image of this repo and make it available to kubernetes
  for deployment.


.. code:: bash

   make deploy



Warning: due to tunneling on K8S you can only have 1 Chart deployed in
1 namespace. This can be fixed by adding an ingress with route53
subdomain.

To destroy all your data and redeploy simply run:


.. code:: bash

   make redeploy
