====================
 Logging Extensions
====================

This package is a set of functions that make python logging easier to use. It also
contains the ability to handle the case of logging in the scoop multiprocessing
environment.

Installation
============

The current version can be installed by the command below::

    pip install https://github.com/IGITUGraz/loggingext/archive/v0.3.0.zip

This can also be installed by downloading the source code (i.e. cloning the
repository) and running the following command from the source directory::

    pip install .

Dependencies
============

Apriori there are no dependencies however, `scoop` must be installed if you wish to
use multiprocessing support for scoop.

Modules
=======

loggingext.logsetup
~~~~~~~~~~~~~~~~~~~

This contains functions that aid in setting up loggers across the entire
simulation. It contains 2 functions

1.  create_shared_logger_data
2.  configure_loggers

See the respective documentation for details and the test scripts for examples
