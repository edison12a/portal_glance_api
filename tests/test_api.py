foobar = __import__("glanceapi")

import pytest
import requests

from foobar import api

"""
def capital_case(x):
    return x.capitalize()

def test_capital_case():
    assert capital_case('rory') == 'Rory'
"""
# TODO: Figure out how to mock database objects?
# TODO: set up and tear downs?
# TODO: ...

# config
API = '{}{}'.format(SERVER, ROUTE)


def test_view_asset_response():
    # test if view is returning data
    r = requests.get('{}'.format(API))

    assert r.status_code == 200


def test_view_asset_methods():
    # test methods that are accepted
    pass
