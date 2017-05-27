"""
Setup tools
"""

__author__ = ""
__version__ = ""
__license__ = ""

from setuptools import setup

# example
"""
setup(
    name='flaskr',
    packages=['flaskr'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
"""

from setuptools import setup

setup(
    name='glance',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
