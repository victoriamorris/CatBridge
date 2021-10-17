#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ====================
#       Set-up
# ====================

# Import required modules
import re


__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'


# ====================
#  Regular expressions
# ====================


RE_ISBN10 = re.compile(r'\b(?=(?:[0-9]+[\- ]?){10})[0-9]{9}[0-9X]\b|'
                       r'\b(?=(?:[0-9]+[\- ]?){13})[0-9]{1,5}[\- ][0-9]+[\- ][0-9]+[\- ][0-9X]\b')
RE_ISBN13 = re.compile(r'\b97[89][0-9]{10}\b|'
                       r'\b(?=(?:[0-9]+[\- ]){4})97[89][\- 0-9]{13}[0-9]\b')


# ====================
#       Classes
# ====================


class Isbn(object):

    def __init__(self, content):
        self.isbn = re.sub(r'X(?!$)', '', re.sub(r'[^0-9X]', '', content.upper()))

    def __str__(self):
        return self.isbn

    def trim(self):
        if len(self.isbn) > 13:
            self.isbn = self.isbn[:13]
        if 10 < len(self.isbn) < 13:
            self.isbn = self.isbn[:10]

    def convert(self):
        if is_isbn_10(self.isbn):
            self.isbn = isbn_convert(self.isbn)

# ====================
#      Functions
# ====================


def isbn_10_check_digit(nine_digits):
    """Function to get the check digit for a 10-digit ISBN"""
    if len(nine_digits) != 9:
        return None
    try:
        int(nine_digits)
    except Exception:
        return None
    remainder = int(sum((i + 2) * int(x) for i, x in enumerate(reversed(nine_digits))) % 11)
    if remainder == 0:
        tenth_digit = 0
    else:
        tenth_digit = 11 - remainder
    if tenth_digit == 10:
        tenth_digit = 'X'
    return str(tenth_digit)


def isbn_13_check_digit(twelve_digits):
    """Function to get the check digit for a 13-digit ISBN"""
    if len(twelve_digits) != 12:
        return None
    try:
        int(twelve_digits)
    except Exception:
        return None
    thirteenth_digit = 10 - int(sum((i % 2 * 2 + 1) * int(x) for i, x in enumerate(twelve_digits)) % 10)
    if thirteenth_digit == 10:
        thirteenth_digit = '0'
    return str(thirteenth_digit)


def isbn_10_check_structure(isbn10):
    """Function to check the structure of a 10-digit ISBN"""
    return True if re.match(RE_ISBN10, isbn10) else False


def isbn_13_check_structure(isbn13):
    """Function to check the structure of a 13-digit ISBN"""
    return True if re.match(RE_ISBN13, isbn13) else False


def is_isbn_10(isbn10):
    """Function to validate a 10-digit ISBN"""
    isbn10 = re.sub(r'[^0-9X]', '', isbn10.replace('x', 'X'))
    if len(isbn10) != 10:
        return False
    return False if isbn_10_check_digit(isbn10[:-1]) != isbn10[-1] else True


def is_isbn_13(isbn13):
    """Function to validate a 13-digit ISBN"""
    isbn13 = re.sub(r'[^0-9X]', '', isbn13.replace('x', 'X'))
    if len(isbn13) != 13:
        return False
    if isbn13[0:3] not in ('978', '979'):
        return False
    return False if isbn_13_check_digit(isbn13[:-1]) != isbn13[-1] else True


def isbn_convert(isbn10):
    """Function to convert a 10-digit ISBN to a 13-digit ISBN"""
    if not is_isbn_10(isbn10):
        return None
    return '978' + isbn10[:-1] + isbn_13_check_digit('978' + isbn10[:-1])
