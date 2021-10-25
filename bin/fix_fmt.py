#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to convert FMT control field into a data field with two blank indicators
and subfield 'a' within one or more file(s) of MARC records"""

from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'fix_fmt'
SUMMARY = 'A utility to convert FMT control field into a data field with two blank indicators and subfield \'a\'.'


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
            date_time_message(f'Reading file {str(file)}')
            reader = MARCReader(file)
            head, tail = os.path.split(file)
            writer = MARCWriter(os.path.join(head, f'fix-{tail}'))
            for record in reader:
                output_record = Record(leader=record.leader)
                for field in record:
                    if field.tag == 'FMT' and hasattr(field, 'data'):
                        output_record.add_field(Field(tag='FMT', indicators=[' ', ' '], subfields=['a', field.data]))
                    else:
                        output_record.add_field(field)
                writer.write(output_record)

            writer.close()
            reader.close()
    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
