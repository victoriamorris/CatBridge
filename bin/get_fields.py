#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to retrieve specified fields and subfields from a file of MARC records"""

import getopt
from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'get_fields'
USAGE = 'A utility to extract specified fields and subfields from a file of MARC records'
SUMMARY = 'Extract fields and subfields specified in <config_file> from <input_file> and write to <output_file>'

FIELDS_TO_NORMALIZE = ['001', '010', '015', '020', '021', '022', '024']


def main(argv=None):

    if argv is None:
        name = str(sys.argv[1])

    re_config = re.compile(r'^([0-9A-Z]{3})\s*\$?\s*([a-z0-9]*)\s*$')
    cb = CatBridge(NAME, USAGE, SUMMARY)
    print(repr(cb))
    cb.add_opts(OrderedDict([
        ('trim', ['Trim subfields & normalize whitespace', False]),
        ('isbn', ['Validate and normalize ISBNs and other control numbers', False]),
        ('rid', ['Include record ID as the first column of the output file', False]),
        ('delim=', ['Specify the delimiter to be used to separate multiple subfields\n'
                    '\t\t\tIf not specified, default is a single white space', ' ']),
    ]))
    try:
        opts, args = getopt.getopt(argv, ''.join([f'{a}:' for a in cb.args]), [o for o in cb.opts.keys()])
    except getopt.GetoptError as err:
        return date_time_exit(f'Error: {err}')
    if opts is None or not opts:
        cb.hint()
    cb.parse_args(opts)
    logging.debug(repr(cb.args))
    logging.debug(repr(cb.opts))

    # Check file locations
    for f in ['i', 'c']:
        logging.info(f'File role {f} location {str(cb.args[f][1])}')
        if cb.args[f][1] and not os.path.isfile(cb.args[f][1]):
            logging.info(f'File role {f} location {str(cb.args[f][1])}')
            raise CBError(f'Error: Could not locate {cb.args[f][0]} at {str(cb.args[f][1])}')

    # Files look ok: start program
    date_time_message('Starting processing')

    fields_to_find = {}

    cfile = open(cb.args['c'][1], mode='r', encoding='utf-8', errors='replace')
    for lineno, line in enumerate(cfile):
        line = line.strip()
        m = re_config.match(line)
        if not m:
            raise CBError(f'Error at line {str(lineno)} of config file: '
                          f'line {line} does not match pattern {str(re_config)}')
        field, subfields = m[1], m[2]
        if field not in fields_to_find:
            fields_to_find[field] = ''
        if subfields != '':
            fields_to_find[field] += f'|{subfields}'
        else:
            fields_to_find[field] += '|!'
    cfile.close()

    delim = cb.opts['delim='][1]
    isbn = cb.opts['isbn'][1]
    trim = cb.opts['trim'][1]
    rid = cb.opts['rid'][1]

    reader = MARCReader(cb.args['i'][1])
    ofile = open(cb.args['o'][1], mode='w', encoding='utf-8', errors='replace')
    all_fields = list(fields_to_find.keys())
    logging.info(f'Search target: {repr(fields_to_find)}')

    for record in reader:
        try:
            record_id = record['001'].data.strip()
        except KeyError:
            logging.warning(f'Record lacking record id at position {str(reader.count)}')
            record_id = '[No record ID]'
        for field in record.get_fields(*all_fields):
            tag = field.tag
            for f_subs in fields_to_find[tag].strip('|').split('|'):
                if f_subs == '!':
                    s = delim.join(field.get_subfields(normalize=trim, cn=isbn))
                else:
                    s = delim.join(field.get_subfields(*list(f_subs), normalize=trim, cn=isbn))
                if s == '':
                    continue
                if rid:
                    s = f'{record_id}\t{s}'
                ofile.write(f'{s}\n')

    for f in [reader, ofile]:
        f.close()

    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
