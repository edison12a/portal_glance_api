api docs
--

config
--
# database details
username='username'
password='password'
ip_local='dev_database_ip'
ip_prod='prodction_database_ip'
dev_db_name='development_database_anme'
prod_db_name='production_database_name'


server setup
--
tested on ubuntu 14.04

sudo apt-get update
sudo apt-get install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx



postgres database set up
--

Commands below for toy database setup in postgres. ubuntu.
# make function for checkcing/setting db
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

.. code-block:: cmd

    listen_addresses = '*'


Next open `pg_hba.conf` and add the below lines to the top of the file.

.. code-block:: cmd

    host all all 192.168.0.0/24 md5
    host all all 0.0.0.0/0 md5
