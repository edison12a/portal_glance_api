app docs
--

config
--
Glance api configuration is brokwn up between 2 files. `config/settings.py` and `config/cred.py`


cred.py contains all credential information and is decoupled for portability. For structure refer to `EXAMPLE_cred.py`.

settings.py manages all of the api's config.
