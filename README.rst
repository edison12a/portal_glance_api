IN DEVELOPMENT

Glance
=====================

Glance is a management system for digital items. Using images to represent various forms of data. Video files, images, documents, source code etc.

Features
---------

Portfolio style display of digital items.

User collections and tagging for storage and retrieval.

:AWS Services:
  AWS s3 backed storage.
  AWS ReKognition.

Installation
------------

A postgresql database needs to be set up prior.

Active AWS s3 account.

Use miniconda for env, environment.yml

.. code-block:: cmd

    $ cd dev-glance-api
    $ conda env create
    $ source activate glance-api-env

Run api.py to get the web api running.

.. code-block:: cmd

    (glance-api-env)$ cd glance-api
    (glance-api-env)$ python api.py

Api entry point is **http://[localhost]/glance/api**

Webapp **http://[localhost]/5000**

Extended Documentation & Tests
-------------

`User Guide`_

`API docs`_

`APP docs`_


Tests
-------------

Running tests, while in project root.

.. code-block:: python

    >>> python setup.py test
