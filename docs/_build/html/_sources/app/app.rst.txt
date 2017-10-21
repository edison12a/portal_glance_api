App
==============

[Description]

----

Tech Stack
----------

* AWS S3
* Flask
* Nginx


----

Deployment
================

Config
------

Glance api configuration is broken up between 2 files. ``config/settings.py`` and ``config/cred.py``

**settings.py**
  settings.py manages all of the api's config.

**cred.py**
  cred.py contains all credential information and is decoupled for portability. For structure refer to `EXAMPLE_cred.py`.
