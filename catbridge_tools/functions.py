import argparse
from collections import OrderedDict
import datetime
import gc
import glob
import os
import sys
import time
from functools import wraps
from catbridge_tools.isbn_tools import *
from catbridge_tools.logs import *

ARGS = {
    'i': lambda parser: parser.add_argument('-i', metavar='<input_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to input file'),
    'i+': lambda parser: parser.add_argument('-i', metavar='<input_file>', required=True, action='store', type=str,
                                             nargs='+', help='path to input file(s)'),
    'o': lambda parser: parser.add_argument('-o', metavar='<output_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to output file'),
    'c': lambda parser: parser.add_argument('-c', metavar='<config_file>', required=True, action='store', type=str,
                                            nargs=1, help='path to config file'),
}

OPTS = OrderedDict([
    ('debug', ['Debug mode', False]),
    ('help', ['Show help message and exit', False]),
])


class CBError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, value):
        logging.error(str(value))
        self.value = value

    def __str__(self):
        return repr(self.value)


class CatBridge:

    def __init__(self, name: str, summary: str, args: list) -> None:
        self.name = name
        self.summary = summary
        self.info()
        self.parser = argparse.ArgumentParser(prog=name)
        for a in args:
            ARGS[a](self.parser)
        self.parser.add_argument('--debug', required=False, action='store_true', help='debug mode'),

    def __repr__(self) -> str:
        return(f'========================================\n{self.name}\n'
               f'========================================\n{self.summary}\n')

    def info(self) -> None:
        logging.info(self.name)
        print(repr(self))

    def parse_args(self, argv) -> argparse.Namespace:
        if len(argv) == 0:
            self.parser.print_help()
            logging.info('No options set')
            date_time_exit(message='Exiting')
        args = self.parser.parse_args()
        logging.debug(f'Command-line arguments: {repr(args)}')
        if args.debug:
            logger.setLevel(logging.DEBUG)
            logging.info('Logging level set to DEBUG')
        return args


def check_file_location(to_check, role):
    for file in glob.glob(to_check):
        if not os.path.isfile(file):
            raise CBError(f'Error: Could not locate {role} at {str(file)}')


def timeit_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print('{0:<10}.{1:<8} : {2:<8}'.format(func.__module__, func.__name__, end - start))
        return func_return_val
    return wrapper


def normalize_space(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip()


def log_print(message: str = '', level=logging.INFO, end='\n') -> None:
    logging.log(level, message)
    print(message, end=end)


def date_time_message(message: str = '') -> None:
    """Function to print a message, followed by the current date and time"""
    if message != '':
        logging.info(message)
        print('\n\n{} ...\n----------------------------------------'.format(message))
    print(str(datetime.datetime.now()))


def date_time_exit(message: str = 'All processing complete', prompt: bool = False) -> None:
    """Function to exit the program after displaying the current date and time"""
    date_time_message(message)
    if prompt:
        input('\nPress [Enter] to exit ...')
    sys.exit()
