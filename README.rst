IN DEVELOPMENT

Glance
=====================

Source code for hosting and utilising the Glance digital item management system.

Glance is a management system for digital items.
Using images to represent various forms of data. Video files, images, documents, source code etc.
Searching is done through the use of tagging each item.

App Features:

oortfolio style display of digital items.

user collections and tagging for storage and retrieval.

Api Features:

flask.

postgres database.

aws s3 storage.

aws rekcogntion.


Installation
------------

A postgresql database needs to be set up prior.

Active AWS s3 account and a bucket called `glancestore`.

Use miniconda for env, environment.yml

.. code-block:: cmd

    $ cd dev-glance-api
    $ conda env create
    $ source activate glance-api-env

Run api.py to get the web api running.

.. code-block:: cmd

    (glance-api-env)$ cd glance-api
    (glance-api-env)$ python api.py

Entry point is **http://[localhost]/glance/api**

Extended Documentation & Tests
-------------

`User Guide`_

`API docs`_

`APP docs`_

Running tests, while in project root.

.. code-block:: python

    >>> python setup.py test
