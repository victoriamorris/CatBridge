from collections import OrderedDict
import datetime
import re
import sys
import time
from functools import wraps
from catbridge_tools.logs import *

ARGS = OrderedDict([
    ('i', ['input_file', None]),
    ('o', ['output_file', None]),
    ('c', ['config_file', None]),
])

OPTS = OrderedDict([
    ('debug', ['Debug mode', False]),
    ('help', ['Show help message and exit', False]),
])


class CBError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class CatBridge:

    def __init__(self, name: str, usage: str, summary: str) -> None:
        self.name = name
        self.usage = usage
        self.summary = summary
        self.opts = OrderedDict([(o, OPTS[o]) for o in OPTS])
        self.args = OrderedDict([(a, ARGS[a]) for a in ARGS])

    def __repr__(self) -> str:
        return(f'========================================\n{self.name}\n'
               f'========================================\n{self.usage}\n')

    def add_args(self, args: OrderedDict) -> None:
        self.args.update(args)

    def add_opts(self, opts: OrderedDict) -> None:
        self.opts = OrderedDict(opts)
        self.opts.update(OPTS)

    def hint(self) -> None:
        """Function to print information about the script"""
        args = self.args
        opts = self.opts
        print('Correct syntax is:\n')
        print(f'{self.name} {" ".join(f"-{a} <{args[a][0]}>" for a in args)} [options]\n')
        print(f'{self.summary}\n')
        for a in args:
            print(f'\t-{a}\tPath to {args[a][0].replace("_", " ")}')
        print('\nUse quotation marks (") around arguments which contain spaces')
        print('\nOptions:')
        for o in opts:
            print(f'\t--{(o + "          ")[:10]}\t{opts[o][0]}')
        print('\n')
        date_time_exit(message='')

    def parse_args(self, opts: dict) -> None:
        for opt, arg in opts:
            opt = opt.strip('-')
            if opt == 'help':
                self.hint()
            elif opt == 'debug':
                logger.setLevel(logging.DEBUG)
            elif opt + '=' in self.opts and arg:
                self.opts[opt + '='][1] = arg
            elif opt in self.opts:
                self.opts[opt][1] = True
            elif opt in self.args:
                self.args[opt][1] = arg
            else:
                logging.error(f'Error: Option {opt} not recognised')
                raise CBError(f'Error: Option {opt} not recognised')


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


def date_time_message(message: str = '') -> None:
    """Function to print a message, followed by the current date and time"""
    if message != '':
        print('\n\n{} ...\n----------------------------------------'.format(message))
    print(str(datetime.datetime.now()))


def date_time_exit(message: str = 'All processing complete', prompt: bool = False) -> None:
    """Function to exit the program after displaying the current date and time"""
    date_time_message(message)
    if prompt:
        input('\nPress [Enter] to exit ...')
    sys.exit()
