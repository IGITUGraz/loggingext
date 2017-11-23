from loggingext.logsetup import create_shared_logger_data, configure_loggers
import os
import logging

log_directory = 'tests/single_proc_log_dir'
try:
    os.mkdir(log_directory)
except FileExistsError:
    pass

logger = logging.getLogger('testlogger')
create_shared_logger_data(logger_names=['testlogger'], log_levels=['INFO'], log_to_consoles=[True],
                          sim_name='testlogger', log_directory=log_directory)

configure_loggers()

logger.debug("TEST LOGGING MESSAGE")
logger.info("TEST LOGGING MESSAGE")
logger.warning("TEST LOGGING MESSAGE")
logger.error("TEST LOGGING MESSAGE")
