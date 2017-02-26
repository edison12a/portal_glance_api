IN DEVELOPMENT

Glance Api
=========================

Rest api code for glance.

Code Examples
---

.. code-block:: python

    >>> code = {'code': ['sample', 'code']}

Installation
------------

A postgresql database needs to be set up prior.

use miniconda for env

.. code-block:: cmd

    $ cd dev-glance-api
    $ conda env create
    $ source activate glance-api-env

Run api.py to get the web api running.

.. code-block:: cmd

    (glance-api-env)$ cd glance-api
    (glance-api-env)$ python api.py

Documentation & Tests
-------------

Extended API docs

Running tests

.. code-block:: python
    >>> test = {'test': ['test', 'test']}
