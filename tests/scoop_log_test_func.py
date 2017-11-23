from loggingext.logsetup import configure_loggers
import logging
from time import sleep

logger = logging.getLogger('scooploggertest.func')


def map_function(int_arg):
    configure_loggers()

    log_message = "TEST LOGGING MESSAGE {}".format(int_arg)
    logger.debug(log_message)
    logger.info(log_message)
    logger.warning(log_message)
    logger.error(log_message)
    sleep(0.2)
