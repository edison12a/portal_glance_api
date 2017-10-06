Api
===================

[Description]

----

Tech Stack
----------


* Postgres
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

server setup
------------

tested on ubuntu 14.04

sudo apt-get update
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx


Postgres set up
---------------

Commands below for toy database setup in postgres. ubuntu.

"""
Set up dev database, if False

sudo -u postgres psql
CREATE DATABASE glance;
CREATE USER glance_user WITH PASSWORD 'password';
ALTER ROLE glance_user SET client_encoding TO 'utf8';
ALTER ROLE glance_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE glance_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE glance TO glance_user;
"""

if hosting postgresql on a different server to the glancec api. a few edits need
to be made in `postgresql.conf` and `pg_hba.conf`.

First `cd` to postgresql installtion dir. For me on ubuntu its
`etc/postgresql/9.5/main`
open `postgresql.conf` and find the line `#listen_addresses = 'localhost'`.
Uncomment it and replace `localhost` with `*`.

::

    listen_addresses = '*'


Next open `pg_hba.conf` and add the below lines to the top of the file.

::

    host all all 192.168.0.0/24 md5
    host all all 0.0.0.0/0 md5


Celery Set up
---------------

Init-script: celeryd

1) 

Create /etc/init.d/celeryd with the content from https://github.com/celery/celery/blob/master/extra/generic-init.d/celeryd

"""
sudo nano /etc/init.d/celeryd

Copy-paste code from celery repo to the file

Save celeryd (CTR+X, y, Enter from nano)

Run following commands from the terminal:

sudo chmod 755 /etc/init.d/celeryd
sudo chown root:root /etc/init.d/celeryd
"""

2)

configuration

Create /etc/default/celeryd

Example:

"""
CELERY_BIN="project/venv/bin/celery"

# App instance to use
CELERY_APP="project_django_project"

# Where to chdir at start.
CELERYD_CHDIR="/home/username/project/"

# Extra command-line arguments to the worker
CELERYD_OPTS="--time-limit=300 --concurrency=8"

# %n will be replaced with the first part of the nodename.
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists (e.g., nobody).
CELERYD_USER="username"
CELERYD_GROUP="username"

# If enabled pid and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1

export SECRET_KEY="foobar"
"""

Activate workers

"""
sudo /etc/init.d/celeryd start
sudo /etc/init.d/celeryd status
sudo /etc/init.d/celeryd stop
"""