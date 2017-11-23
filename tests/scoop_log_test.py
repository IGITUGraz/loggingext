from loggingext.logsetup import create_shared_logger_data, configure_loggers
import os
import logging

from scoop_log_test_func import map_function

try:
    from scoop.futures import map
    import scoop
except ImportError as E:
    raise RuntimeError("The scoop log test requires the scoop feature to be installed via \n"
                       "pip install .[scoop] --process-dependency-links")

if not scoop.IS_RUNNING:
    raise RuntimeError("This test is to be run using scoop i.e\n"
                       "python -m scoop [scoop options] tests/scoop_log_test.py")

log_directory = 'tests/scoop_proc_log_dir'
try:
    os.mkdir(log_directory)
except FileExistsError:
    pass

logger = logging.getLogger('scooploggertest.main')


def main():
    create_shared_logger_data(logger_names=['scooploggertest'], log_levels=['INFO'], log_to_consoles=['originonly'],
                              sim_name='testlogger', log_directory=log_directory)
    configure_loggers()
    res = list(map(map_function, range(100)))


if __name__ == '__main__':
    main()
