IN DEVELOPMENT

Glance Api
=========================

database and web api for digital asset management, storage and retrieval.

Code Examples
---

.. code-block:: python

    >>> code = {'code': ['sample', 'code']}

Installation
------------

A postgresql database needs to be set up prior.

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

Documentation & Tests
-------------

Extended API docs

Running tests

.. code-block:: python
    >>> test = {'test': ['test', 'test']}
