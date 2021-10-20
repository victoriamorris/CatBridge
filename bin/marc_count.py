#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to count the number of records present within one or more file(s) of MARC records"""

from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'marc_count'
SUMMARY = 'A utility to count the number of records present within one or more file(s) of MARC records'


def main(argv=None):

    if argv is None:
        name = str(sys.argv[1])

    cb = CatBridge(NAME, SUMMARY, ['i+', ])
    args = cb.parse_args(argv)
    total = 0

    for a in args.i:
        file_list = glob.glob(a)
        for file in file_list:
            if not os.path.isfile(file):
                raise CBError(f'Error: Could not locate {str(file)}')
            reader = MARCReader(file)
            file_total = len(reader)
            total += file_total
            log_print(f'File {os.path.basename(file)} contains {str(file_total)} records ')
            reader.close()
    print(f'Total number of records read: {str(total)}')
    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
