from setuptools import setup

from loggingext import __version__ as FULL_VERSION

"""
This file installs the ltl package.
Note that it does not perform any installation of the documentation. For this, follow the specified procedure in the
 README. For updating the version, update MAJOR_VERSION and FULL_VERSION in ltl/version.py
"""


setup(
    name="loggingext",
    version=FULL_VERSION,
    packages=['loggingext'],
    author="Arjun Rao, Anand Subramoney",
    author_email="arjun@igi.tugraz.at, anand@igi.tugraz.at",
    description="This module provides helper functions to make the access to logging"
                " more convenient especially in conjunction with multiprocessing using"
                " the SCOOP package",
    install_requires=[],
    provides=['loggingext'],
)
