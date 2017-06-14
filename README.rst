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

Clone repo.

Use miniconda for env, environment.yml
# TODO: research/automate building requirements.txt from environment.yml??
# or just use pyenv?

.. code-block:: cmd

    $ cd dev-glance-api
    $ conda env create
    $ source activate glance-api-env

setup.py develop
# TODO: research: if i use install none of the modules can find each other...
# why?

setup.py tests

Api config
..........

glance_api/config/config.ini

Run glance_api/api.py to get api running.

.. code-block:: cmd

    (glance-api-env)$ cd glance_api
    (glance-api-env)$ python api.py

http://localhost/glance/api

App config
..........

glance/config/config.ini

Run glance/app.py to get the app running.

.. code-block:: cmd

    (glance-api-env)$ cd glance
    (glance-api-env)$ python app.py



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
