api docs
--

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
