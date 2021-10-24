#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ====================
#       Set-up
# ====================


# Import required modules
import os
import unicodedata
from catbridge_tools.functions import *
from io import BytesIO
from typing import Callable


__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


# ====================
#     Constants
# ====================


LEADER_LENGTH, DIRECTORY_ENTRY_LENGTH = 24, 12
SUBFIELD_INDICATOR, END_OF_FIELD, END_OF_RECORD = chr(0x1F), chr(0x1E), chr(0x1D)
ALEPH_CONTROL_FIELDS = ['DB ', 'SYS']


# ====================
#     Exceptions
# ====================


class RecordLengthError(Exception):
    def __str__(self): return 'Invalid record length in first 5 bytes of record'


class LeaderError(Exception):
    def __str__(self): return 'Error reading record leader'


class DirectoryError(Exception):
    def __str__(self): return 'Record directory is invalid'


class FieldsError(Exception):
    def __str__(self): return 'Error locating fields in record'


class BaseAddressLengthError(Exception):
    def __str__(self): return 'Base address exceeds size of record'


class BaseAddressError(Exception):
    def __str__(self): return 'Error locating base address of record'


class RecordWritingError(Exception):
    def __str__(self): return 'Error writing record'


# ====================
#      Functions
# ====================


def clean(string):
    if string is None or not string:
        return None
    string = re.sub(r'[\u0022\u055A\u05F4\u2018-\u201F\u275B-\u275E\uFF07]', '\'', string)
    string = re.sub(r'[\u0000-\u001F\u0080-\u009F\u2028\u2029]+', '', string)
    string = re.sub(r'^[:;/\s?$.,\\\])}]|[;/\s$.,\\\[({]+$', '', string.strip())
    string = re.sub(r'\s+', ' ', string).strip()
    if string is None or not string:
        return None
    return unicodedata.normalize('NFC', string)


# ====================
#       Classes
# ====================


class MARCReader(object):

    def __init__(self, path_to_file):
        self.count = 0
        self.processed = 0
        self.path_to_file = path_to_file
        self.file_handle = open(path_to_file, mode='rb')
        self.silent = False

    def __sizeof__(self):
        return os.path.getsize(self.path_to_file)

    def __iter__(self):
        return self

    def __len__(self):
        self.silent = True
        for record in self:
            continue
        return self.count - 1

    def close(self):
        self.count -= 1
        if not self.silent:
            log_print(f'100% [{str(self.count)} records] processed')
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def __next__(self):
        self.count += 1
        first5 = self.file_handle.read(5)
        if not first5:
            raise StopIteration
        if len(first5) < 5:
            raise RecordLengthError
        self.processed += int(first5)
        if not self.silent:
            if self.count % 1000 == 0:
                print(f'{str(int(100*self.processed / self.__sizeof__()))}% [{str(self.count)} records] processed',
                      end='\r')
                if self.count % 100000 == 0:
                    gc.collect()
        return Record(first5 + self.file_handle.read(int(first5) - 5))


class MARCWriter(object):

    def __init__(self, path_to_file):
        self.count = 0
        self.processed = 0
        self.path_to_file = path_to_file
        self.file_handle = open(path_to_file, mode='wb')
        self.silent = False

    def write(self, record):
        if not isinstance(record, Record):
            raise RecordWritingError
        self.file_handle.write(record.as_marc())

    def close(self):
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None


class Record(object):
    def __init__(self, data: bytes = None, leader=' ' * LEADER_LENGTH):
        self.leader = '{}22{}4500'.format(leader[0:10], leader[12:20])
        self.fields = list()
        self.pos = 0
        if data and len(data) > 0:
            self.decode_marc(data)

    def __getitem__(self, tag):
        fields = self.get_fields(tag)
        if len(fields) > 0:
            return fields[0]
        return None

    def __contains__(self, tag):
        fields = self.get_fields(tag)
        return len(fields) > 0

    def __iter__(self):
        self.__pos = 0
        return self

    def __next__(self):
        if self.__pos >= len(self.fields):
            raise StopIteration
        self.__pos += 1
        return self.fields[self.__pos - 1]

    def __repr__(self):
        text_list = ['=LDR  {}'.format(self.leader)]
        text_list.extend([str(field) for field in self.fields])
        return '\n'.join(text_list) + '\n'

    def __sizeof__(self):
        return len(self.get_fields())

    def get_fields(self, *args, indicators=None):
        if len(args) == 0:
            return self.fields
        if not indicators:
            return [f for f in self.fields if f.tag in args]
        return [f for f in self.fields if f.tag in args
                and (indicators[0] == '*' or f.indicators[0].replace('#', ' ') in ['*', indicators[0].replace('#', ' ')])
                and (indicators[1] == '*' or f.indicators[1].replace('#', ' ') in ['*', indicators[1].replace('#', ' ')])]

    def add_field(self, *fields):
        self.fields.extend(fields)

    def decode_marc(self, marc):
        # Extract record leader
        try:
            self.leader = marc[0:LEADER_LENGTH].decode('ascii')
        except Exception as err:
            logging.warning(f'Encountered record with Leader that could not be processed: {err}')
        if len(self.leader) != LEADER_LENGTH:
            raise LeaderError

        # Extract the byte offset where the record data starts
        base_address = int(marc[12:17])
        if base_address <= 0:
            raise BaseAddressError
        if base_address >= len(marc):
            raise BaseAddressLengthError

        # Extract directory
        # base_address-1 is used since the directory ends with an END_OF_FIELD byte
        directory = marc[LEADER_LENGTH:base_address - 1].decode('ascii')

        # Determine the number of fields in record
        if len(directory) % DIRECTORY_ENTRY_LENGTH != 0:
            raise DirectoryError
        field_total = len(directory) / DIRECTORY_ENTRY_LENGTH

        # Add fields to record using directory offsets
        field_count = 0
        while field_count < field_total:
            entry_start = field_count * DIRECTORY_ENTRY_LENGTH
            entry_end = entry_start + DIRECTORY_ENTRY_LENGTH
            entry = directory[entry_start:entry_end]
            entry_tag = entry[0:3]
            entry_length = int(entry[3:7])
            entry_offset = int(entry[7:12])
            entry_data = marc[base_address + entry_offset:base_address + entry_offset + entry_length - 1]

            # Check if tag is a control field
            if str(entry_tag) < '010' and entry_tag.isdigit():
                field = Field(tag=entry_tag, data=entry_data.decode('utf-8'))
            elif str(entry_tag) in ALEPH_CONTROL_FIELDS:
                field = Field(tag=entry_tag, data=entry_data.decode('utf-8'))

            else:
                subfields = list()
                subs = entry_data.split(SUBFIELD_INDICATOR.encode('ascii'))
                # Missing indicators are recorded as blank spaces.
                # Extra indicators are ignored.
                try:
                    subs[0] = subs[0].decode('ascii') + '  '
                except Exception:
                    subs[0] = '   '
                first_indicator, second_indicator = subs[0][0], subs[0][1]

                for subfield in subs[1:]:
                    if len(subfield) == 0:
                        continue
                    try:
                        code, data = subfield[0:1].decode('ascii'), subfield[1:].decode('utf-8', 'strict')
                    except Exception:
                        pass
                    else:
                        subfields.append(code)
                        subfields.append(data)
                field = Field(
                    tag=entry_tag,
                    indicators=[first_indicator, second_indicator],
                    subfields=subfields,
                )
            self.add_field(field)
            field_count += 1

        if field_count == 0:
            raise FieldsError

    def as_marc(self):
        fields, directory = b'', b''
        offset = 0

        for field in self.fields:
            field_data = field.as_marc()
            fields += field_data
            if field.tag.isdigit():
                directory += ('%03d' % int(field.tag)).encode('utf-8')
            else:
                directory += ('%03s' % field.tag).encode('utf-8')
            directory += ('%04d%05d' % (len(field_data), offset)).encode('utf-8')
            offset += len(field_data)

        directory += END_OF_FIELD.encode('utf-8')
        fields += END_OF_RECORD.encode('utf-8')
        base_address = LEADER_LENGTH + len(directory)
        record_length = base_address + len(fields)
        strleader = '%05d%s%05d%s' % (record_length, self.leader[5:12], base_address, self.leader[17:])
        leader = strleader.encode('utf-8')
        return leader + directory + fields

    def id(self) -> str:
        try:
            self.id = self['001'].data.strip()
        except KeyError:
            logging.warning(f'Record lacking record id with title {str(self["245"]) or "[No title either!]"}')
            self.id = '[No record ID]'
        return self.id


class Field(object):

    def __init__(self, tag, indicators=None, subfields=None, data=''):
        if indicators is None:
            indicators = []
        if subfields is None:
            subfields = []
        indicators = [str(x) for x in indicators]

        # Normalize tag to three digits
        self.tag = '%03s' % tag

        # Check if tag is a control field
        if self.tag < '010' and self.tag.isdigit():
            self.data = str(data)
        elif self.tag in ALEPH_CONTROL_FIELDS:
            self.data = str(data)
        else:
            self.indicator1, self.indicator2 = self.indicators = indicators
            self.subfields = subfields

    def __iter__(self):
        self.__pos = 0
        return self

    def __getitem__(self, subfield):
        subfields = self.get_subfields(subfield)
        if len(subfields) > 0:
            return subfields[0]
        return None

    def __contains__(self, subfield):
        subfields = self.get_subfields(subfield)
        return len(subfields) > 0

    def __next__(self):
        if not hasattr(self, 'subfields'):
            raise StopIteration
        while self.__pos + 1 < len(self.subfields):
            subfield = (self.subfields[self.__pos], self.subfields[self.__pos + 1])
            self.__pos += 2
            return subfield
        raise StopIteration

    def __repr__(self):
        if self.is_control_field() or self.tag in ALEPH_CONTROL_FIELDS:
            return '={}  {}'.format(self.tag, self.data.replace(' ', '#'))
        text = '={}  '.format(self.tag)
        for indicator in self.indicators:
            if indicator in (' ', '#'):
                text += '#'
            else:
                text += indicator
        text += ' '
        for subfield in self:
            text += '${}{}'.format(subfield[0], subfield[1])
        return text

    def str(self, subfields=''):
        if self.is_control_field() or self.tag in ALEPH_CONTROL_FIELDS:
            return self.data.replace(' ', '#')
        return ' '.join(subfield[1] for subfield in self if subfield[0] in subfields)

    def get_subfields(self, *codes):
        if self.is_control_field() or self.tag in ALEPH_CONTROL_FIELDS:
            return [self.data, ]
        values = []
        for subfield in self:
            if len(codes) == 0 or not codes or subfield[0] in codes:
                values.append(str(subfield[1]))
        return values

    def is_control_field(self):
        if self.tag < '010' and self.tag.isdigit():
            return True
        if self.tag in ALEPH_CONTROL_FIELDS:
            return True
        return False

    def as_marc(self):
        if self.is_control_field():
            return (self.data + END_OF_FIELD).encode('utf-8')
        marc = self.indicator1 + self.indicator2
        for subfield in self:
            marc += SUBFIELD_INDICATOR + subfield[0] + subfield[1]
        return (marc + END_OF_FIELD).encode('utf-8')


def map_records(f: Callable, *files: BytesIO) -> None:
    """Applies a given function to each record in a batch"""
    for file in files:
        list(map(f, MARCReader(file)))


def is_control_field_tag(tag: str) -> bool:
    """Function to test whether a tag denotes a control field"""
    if not tag:
        return False
    if tag < '010' and tag.isdigit():
        return True
    if tag in ALEPH_CONTROL_FIELDS:
        return True
    return False