#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to count the number of records present within one or more file(s) of MARC records"""

from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'marc_check'
SUMMARY = 'A utility a to check the structural validity MARC records, and isolate those found to be flawed.'


def main(argv=None):

    if argv is None:
        name = str(sys.argv[1])

    cb = CatBridge(NAME, SUMMARY, ['i+', ])
    args = cb.parse_args(argv)

    for a in args.i:
        file_list = glob.glob(a)
        for file in file_list:
            if not os.path.isfile(file):
                raise CBError(f'Error: Could not locate {str(file)}')
            print('\n')
            log_print(f'Checking file {os.path.basename(file)}')
            file_errors = 0
            reader = MARCReaderTentative(file)
            fname, ext = os.path.splitext(file)
            writer = MARCWriter(f'{fname}_ok{ext}')
            efile = open(f'{fname}_f.lex', mode='wb')

            for status, message, record in reader:
                file_errors += not int(status)
                if not status:
                    log_print(message)
                    efile.write(record)
                else:
                    writer.write(record)
            efile.close()
            writer.close()
            log_print(f'File {os.path.basename(file)} contains {str(file_errors)} flawed records')
            reader.close()

    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
