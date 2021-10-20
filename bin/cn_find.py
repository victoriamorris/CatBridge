#!/usr/bin/env python
# -*- coding: utf8 -*-

"""Script to extract control numbers from a file of MARC records"""

from catbridge_tools import *

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


NAME = 'cn_find'
SUMMARY = 'A utility to extract control numbers from specified fields and subfields within a file of MARC records'


RE_CONTROL_NUMBERS = {
    'ISBN': re.compile(r'\b(?=(?:[0-9]+[\- ]?){10})[0-9]{9}[0-9Xx]\b|'
                       r'\b(?=(?:[0-9]+[\- ]?){13})[0-9]{1,5}[\- ][0-9]+[\- ][0-9]+[\- ][0-9Xx]\b|'
                       r'\b97[89][0-9]{10}\b|'
                       r'\b(?=(?:[0-9]+[\- ]){4})97[89][\- 0-9]{13}[0-9]\b'),
    'ISBN10': re.compile(r'\b(?=(?:[0-9]+[\- ]?){10})[0-9]{9}[0-9Xx]\b|'
                         r'\b(?=(?:[0-9]+[\- ]?){13})[0-9]{1,5}[\- ][0-9]+[\- ][0-9]+[\- ][0-9Xx]\b'),
    'ISBN13': re.compile(r'\b97[89][0-9]{10}\b|'
                         r'\b(?=(?:[0-9]+[\- ]){4})97[89][\- 0-9]{13}[0-9]\b'),
    'ISSN': re.compile(r'\b[0-9]{4}[ \-]?[0-9]{3}[0-9Xx]\b'),
    'LCCN': re.compile(r'\b[a-z][a-z ][a-z ]?[0-9]{2}[0-9]{6} ?\b'),
    'ISNI': re.compile(r'\b[0]{4}[ \-]?[0-9]{4}[ \-]?[0-9]{4}[ \-]?[0-9]{3}[0-9Xx]\b'),
    'BL001': re.compile(r'\b[0-9]{9}\b'),
    'FAST': re.compile(r'\bfst[0-9]{8}\b'),
    'OCLC': re.compile(r'\(OCoLC\)[0-9]+\b'),
    'BNB':  re.compile(r'\bGB([0-9]{7}|[A-Z][0-9][A-Z0-9][0-9]{4})\b')
}


def clean_isbn(s):
    return re.sub(r'[^0-9X]', '', s.upper())


def clean_issn(s):
    s = re.sub(r'[^0-9X]', '', s.upper())
    return f'{s[:4]}-{s[4:]}'


CONTROL_NUMBER_CLEANING = {
    'ISBN': clean_isbn,
    'ISBN10': clean_isbn,
    'ISBN13': clean_isbn,
    'ISSN': clean_issn,
    'ISNI': clean_isbn,
}


def main(argv=None):

    if argv is None:
        name = str(sys.argv[1])

    re_config = re.compile(r'^([0-9A-Z]{3})\s*\$?\s*([a-z0-9]?)\s*\t(.*?)\s*$')
    cb = CatBridge(NAME, SUMMARY, ['i+', 'o', 'c'])
    cb.parser.add_argument('--conv', required=False, action='store_true',
                           help='Convert 10-digit ISBNs to 13-digit form where possible')
    cb.parser.add_argument('--rid', required=False, action='store_true',
                           help='Include record ID as the first column of the output file')
    cb.parser.add_argument('--tidy', required=False, action='store_true',
                           help='Sort and de-duplicate list')

    args = cb.parse_args(argv)

    if args.rid and args.tidy:
        raise CBError(f'Error: options rid and tidy cannot be used at the same time')

    fields_to_find = []

    check_file_location(args.c[0], 'config file')
    date_time_message(f'Reading config file from {str(args.c[0])}')
    cfile = open(args.c[0], mode='r', encoding='utf-8', errors='replace')
    for lineno, line in enumerate(cfile):
        line = line.strip()
        m = re_config.match(line)
        if not m:
            r = str(re_config.pattern).replace('\\\\', '\\')
            raise CBError(f'Error at line {str(lineno)} of config file: '
                          f'line {line} does not match pattern {r}')
        if m[3] in RE_CONTROL_NUMBERS:
            regex = RE_CONTROL_NUMBERS[m[3]]
        else:
            logging.debug(f'Compiling regex {m[3]}')
            try:
                regex = re.compile(m[3])
            except re.error as err:
                raise CBError(f'Error at line {str(lineno)} of config file: '
                              f'{m[3]} is not a valid regular expression: {err}')
        fields_to_find.append((m[1], m[2], m[3], regex))
    cfile.close()
    logging.info(f'Search target: {repr(fields_to_find)}')

    if args.rid:
        logging.info('Including record ID in first column')
    if args.conv:
        logging.info('Converting ISBN-10 to ISBN-13')
    if args.tidy:
        logging.info('Producing tidy output')

    cn, cn_dupes = set(), set()
    ofile = open(args.o[0], mode='w', encoding='utf-8', errors='replace')

    for a in args.i:
        file_list = glob.glob(a)
        for file in file_list:
            if not os.path.isfile(file):
                raise CBError(f'Error: Could not locate {str(file)}')
            date_time_message(f'Processing file {str(file)}')
            reader = MARCReader(file)
            for record in reader:
                for (f, s, r, regex) in fields_to_find:
                    for field in record.get_fields(f):
                        if not s:
                            subfields = field.get_subfields()
                        else:
                            subfields = field.get_subfields(s)
                        for subfield in subfields:
                            for m in regex.finditer(subfield):
                                if r in CONTROL_NUMBER_CLEANING:
                                    t = CONTROL_NUMBER_CLEANING[r](m.group(0))
                                else:
                                    t = m.group(0).strip()
                                if args.conv and is_isbn_10(t):
                                    t = isbn_convert(t)
                                if args.tidy:
                                    if t in cn:
                                        cn_dupes.add(t)
                                    else:
                                        cn.add(t)
                                else:
                                    if args.rid:
                                        t = f'{record.id}\t{t}'
                                    ofile.write(f'{t}\n')
            reader.close()

    if args.tidy:
        for t in sorted(cn):
            ofile.write(f'{t}\n')

    ofile.close()

    if args.tidy:
        head, tail = os.path.split(args.o[0])
        ofile = open(os.path.join(head, f'dp-{tail}'), mode='w', encoding='utf-8', errors='replace')
        for t in sorted(cn_dupes):
            ofile.write(f'{t}\n')
        ofile.close()

    date_time_exit()


if __name__ == "__main__":
    main(sys.argv[1:])
