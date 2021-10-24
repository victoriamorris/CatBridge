#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to count the number of records present within one or more file(s) of MARC records"""

from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'keep_fld'
SUMMARY = 'A utility to keep or delete specified fields within one or more file(s) of MARC records'


def main(argv=None):

    if argv is None:
        name = str(sys.argv[1])

    re_config = re.compile(r'^=(?P<tag>[0-9A-Z]{3})  (?P<ind>[0-9*#][0-9*#])(?P<sfs>(?:\$[a-z0-9*] ?.*?)*)$|'
                           r'^=(?P<control_tag>00[0-9]|[A-Z]{3})(  )?(?P<data>.*?)$')
    r = str(re_config.pattern).replace('\\\\', '\\')
    cb = CatBridge(NAME, SUMMARY, ['i+', 'c'])
    cb.parser.add_argument('--delete', required=False, action='store_true',
                           help='*Delete* fields specified in <config_file>')

    args = cb.parse_args(argv)

    test_record = Record()

    all_fields = set()

    check_file_location(args.c[0], 'config file')
    date_time_message(f'Reading config file from {str(args.c[0])}')
    cfile = open(args.c[0], mode='r', encoding='utf-8', errors='replace')
    for lineno, line in enumerate(cfile):
        line = line.strip()
        if line.startswith('001'):
            continue
        m = re_config.match(line)
        if not m:
            raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                          f'line {line} does not match pattern {r}')
        if m.group('control_tag'):
            if m.group('control_tag') in all_fields:
                raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                              f'field tag {m.group("control_tag")} already specified')
            if not is_control_field_tag(m.group('control_tag')):
                raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                              f'control field contents specified for data field {m.group("control_tag")}')
            all_fields.add(m.group('control_tag'))
            if m.group('data'):
                test_record.add_field(Field(tag=m.group('control_tag'), data=m.group('data')))
            else:
                test_record.add_field(Field(tag=m.group('control_tag'), data='*'))
            continue
        if m.group('tag'):
            if m.group('tag') in all_fields:
                raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                              f'field tag {m.group("tag")} already specified')
            if is_control_field_tag(m.group('tag')):
                raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                              f'data field contents specified for control field {m.group("tag")}')
            all_fields.add(m.group('tag'))
            if m.group('sfs') and len(m.group('sfs').strip()) > 0:
                subfields = []
                for subfield in re.split(r'\$(?=[a-z0-9*])', m.group('sfs').strip()):
                    subfield = subfield.strip()
                    if len(subfield) < 1:
                        continue
                    if len(subfield) == 1:
                        subfields.extend([subfield[0], '.*'])
                        continue
                    code, pattern = subfield[0], subfield[1:]
                    try:
                        re.compile(pattern)
                    except re.error as err:
                        raise CBError(f'Error at line {str(lineno + 1)} of config file: '
                                      f'{pattern} is not a valid regular expression: {err}')
                    subfields.extend([code, pattern])
            else:
                subfields = ['*', '.*']
            test_record.add_field(Field(tag=m.group('tag'), indicators=[m.group('ind')[0], m.group('ind')[1]],
                                        subfields=subfields))
    logging.info(f'Search for records matching:\n\n{str(test_record)}\n')
    cfile.close()

    del_fld = args.delete
    if del_fld:
        logging.info('Specified fields/subfields will be deleted')
    else:
        logging.info('Specified fields/subfields will be kept')

    for a in args.i:
        file_list = glob.glob(a)
        for file in file_list:
            if not os.path.isfile(file):
                raise CBError(f'Error: Could not locate {str(file)}')
            date_time_message(f'Reading file {str(file)}')
            reader = MARCReader(file)
            head, tail = os.path.split(file)
            writer = MARCWriter(os.path.join(head, f'{"d" if del_fld else "k"}-{tail}'))
            for record in reader:
                output_record = Record(leader=record.leader)
                for field in record:
                    tag = field.tag

                    # Always include 001 in output
                    if tag == '001':
                        output_record.add_field(field)
                        continue

                    # Simple case
                    if tag not in test_record:
                        if del_fld:
                            output_record.add_field(field)
                        continue

                    # Control fields
                    if is_control_field_tag(tag):
                        write = False
                        for test_field in test_record.get_fields(tag):
                            if re.search(test_field.data, field.data):
                                write = True
                                break
                        if write ^ del_fld:
                            output_record.add_field(field)
                        continue

                    else:
                        output_subfields = []
                        for test_field in test_record.get_fields(tag, indicators=field.indicators):

                            # Consider subfields individually
                            for subfield in field:
                                write_subfield = False
                                code, content = subfield
                                for test_subfield in test_field:
                                    if test_subfield[0] in [code, '*']:
                                        if re.search(test_subfield[1], content):
                                            write_subfield = True
                                            break
                                if write_subfield ^ del_fld:
                                    output_subfields.extend(subfield)
                            if output_subfields:
                                output_record.add_field(Field(tag=tag, indicators=field.indicators,
                                                              subfields=output_subfields))
                writer.write(output_record)

            writer.close()
            reader.close()
    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
