"""
This module contains functions that help conveniently configure loggers. Currently
there are 2 functions create_shared_logger_data and configure_loggers that allow
convenient configuration of loggers in a single-process / scoop-multiprocessing
environment.
"""

import os
import logging
import logging.config

try:
    import scoop
    import scoop.shared
except ImportError as E:
    with_scoop = False
else:
    with_scoop = True

import socket
import copy


def create_shared_logger_data(logger_names, log_levels, log_to_consoles,
                              sim_name, log_directory):
    """
    This function must be called to create a shared copy of information that will be
    required to setup logging across processes. This must be run exactly once in the
    root process. Note that it is not necessary for you to be running SCOOP in order to
    use this function. This will work even in the single process case where you don't
    run SCOOP in which case it will create global variables that store the logger data.

    :param logger_names: This is a list of names of the loggers whose output you're
        interested in. The settings to a particular logger propagate to all sub-loggers

    :param log_levels: This is the list containing the log levels of the respective
        loggers. It must be of the same legnth as `logger_names`

    :param log_to_consoles: This is a list of values each of which is either boolean
        True or False, or the string 'originonly'. This list must be of the same legnth
        as `logger_names`. The logger correspondingly performs the following handling
        on the values:

        If `True`, then the logger always outputs to the console

        If `False`, then the logger never outputs to the console.

        If `'originonly'` then only the logger instance in the root process outputs to
        stdout. In case of a single process environment, it has the same behaviour as
        `True`

        Note that the loggers as ALWAYS recorded to file irrespective of how they are
        configured with regards to console printing. Also note that with SCOOP, output
        to stdout on any worker gets directed to the console of the main process.

    :param sim_name: This is a string that is used as a prefix when creating the log
        files. Short for simulation name.

    :param log_directory: This is the path of the directory in which the log files will
        be stored. This directory must be a directory which already exists.

    When configured using the :meth:`.configure_loggers` function, the loggers are
    setup to direct their messages to the files and/or the console (whether or not the
    output is printed on the console is dependent on the log_to_consoles option for
    that particular logger). The file names are as follows:

    1.  For the logger of the root process (without SCOOP, there is only the root
        process) , we have `<log_directory>/<sim_name>_LOG.txt` and
        `<log_directory>/<sim_name>_ERROR.txt` for the non-error and error logs
        respectively.
    2.  For loggers of other SCOOP processes, each one directs its output to a distinct
        file by the name `<log_directory>/<sim_name>_<host_name>_<process_id>_LOG.txt`
        and similarly for error logs.
    """

    # process / validate input
    assert len(logger_names) == len(log_levels) == len(log_to_consoles), \
        "The sizes of logger_names, log_levels, log_to_consoles are inconsistent"
    assert all(isinstance(x, str) for x in logger_names), \
        "'logger_names' and must be a list of strings"
    assert os.path.isdir(log_directory), "The log_directory {} is not a valid log directory".format(log_directory)
    assert all(x in [True, False, 'originonly'] for x in log_to_consoles), \
        "log_to_consoles must be either boolean or the string 'originonly'"

    if with_scoop and scoop.IS_RUNNING:
        assert scoop.IS_ORIGIN, \
            "create_shared_logger_data must be called only on the origin worker"
        scoop.shared.setConst(logger_names=logger_names, log_levels=log_levels,
                              sim_name=sim_name, log_directory=log_directory, log_to_consoles=log_to_consoles)
    else:
        global logger_names_global, log_levels_global, log_to_consoles_global
        global sim_name_global, log_directory_global
        logger_names_global = logger_names
        log_levels_global = log_levels
        log_to_consoles_global = log_to_consoles
        sim_name_global = sim_name
        log_directory_global = log_directory


def configure_loggers(exactly_once=False):
    """
    This function configures the loggers using the shared information that was set by
    :meth:`.create_shared_logger_data`. This function must be run at the beginning
    of every function that is parallelized in order to be able to reliably
    configure the loggers.

    You may also wish to call this function in the root process (after calling
    :meth:`.create_shared_logger_data`) to configure the logging for the root process
    before any of the parallelized functions are run.

    :param exactly_once: If the configuration of logging is causing a significant
        overhead per parallelized run (This is a rather unlikely scenario), then this
        value may be set to `True`. When True, the function will configure the loggers
        exactly once per SCOOP worker.
    """

    if exactly_once and configure_loggers._already_configured:
        return

    if with_scoop and scoop.IS_RUNNING:
        # Get shared data from scoop and perform the relevant configuration
        logger_names = scoop.shared.getConst('logger_names', timeout=1.0)
        log_levels = scoop.shared.getConst('log_levels', timeout=1.0)
        log_to_consoles = scoop.shared.getConst('log_to_consoles', timeout=1.0)
        sim_name = scoop.shared.getConst('sim_name', timeout=1.0)
        log_directory = scoop.shared.getConst('log_directory', timeout=1.0)
        if logger_names is None:
            return
    else:
        # Get logger data from global variables and perform the relevant thing
        logger_names = logger_names_global
        log_levels = log_levels_global
        log_to_consoles = log_to_consoles_global
        sim_name = sim_name_global
        log_directory = log_directory_global

    if with_scoop and scoop.IS_RUNNING and not scoop.IS_ORIGIN:
        file_name_prefix = '%s_%s_%s_' % (sim_name, socket.gethostname(), os.getpid())
        log_to_consoles = [False if x == 'originonly' else x for x in log_to_consoles]
    else:
        file_name_prefix = '%s_' % (sim_name,)
        log_to_consoles = [True if x == 'originonly' else x for x in log_to_consoles]

    config_dict_copy = copy.deepcopy(configure_loggers.basic_config_dict)

    config_dict_copy['loggers'] = {}

    # Configuring the output files
    log_fname = os.path.join(log_directory,
                             file_name_prefix + config_dict_copy['handlers']['file_log']['filename'])
    error_fname = os.path.join(log_directory,
                               file_name_prefix + config_dict_copy['handlers']['file_error']['filename'])
    config_dict_copy['handlers']['file_log']['filename'] = log_fname
    config_dict_copy['handlers']['file_error']['filename'] = error_fname

    # Creating logger entries
    for logger_name, log_level, log_to_console in zip(logger_names, log_levels, log_to_consoles):
        config_dict_copy['loggers'][logger_name] = {}
        logger_dict = config_dict_copy['loggers'][logger_name]
        logger_dict['level'] = log_level
        if log_to_console:
            logger_dict['handlers'] = ['console', 'file_log', 'file_error']
        else:
            logger_dict['handlers'] = ['file_log', 'file_error']

    logging.config.dictConfig(config_dict_copy)
    configure_loggers._already_configured = True


configure_loggers._already_configured = False
configure_loggers.basic_config_dict = {
    'version': 1,
    'formatters': {
        'file': {
            'format': '%(asctime)s %(name)s {} %(process)d %(levelname)-8s: %(message)s'.format(socket.gethostname())
        },
        'stream': {
            'format': '%(processName)-10s %(name)s {} %(process)d %(levelname)-8s: %(message)s'.format(
                socket.gethostname())
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'stream',
        },
        'file_log': {
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'LOG.txt',
        },
        'file_error': {
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'ERROR.txt',
            'level': 'ERROR',
        },
    },
    'loggers': {},
    'root': {
        # 'level': 'INFO',
        'handlers': []
    }
}
