#!/usr/bin/env python
# -*- coding: utf8 -*-

# Import required modules
import re
from distutils.core import setup

__author__ = 'Victoria Morris'
__license__ = 'MIT License'
__version__ = '1.0.0'
__status__ = '4 - Beta Development'

# List requirements.
# All other requirements should all be contained in the standard library
requirements = [
    'regex'
]

# Setup
setup(
    console=[
        'bin/cn_find.py',
        'bin/fix_fmt.py',
        'bin/keep_fld.py',
        'bin/marc_check.py',
        'bin/marc_count.py',
    ],
    zipfile=None,
    options={
        'py2exe': {
            'bundle_files': 0,
        }
    },
    name='catbridge_tools',
    version='1.0.0',
    author='Victoria Morris',
    url='https://github.com/victoriamorris/CatBridge',
    license='MIT',
    description='Tools for working with MARC data in Catalogue Bridge.',
    long_description='Tools for working with MARC data in Catalogue Bridge.',
    packages=['catbridge_tools'],
    scripts=[
        'bin/cn_find.py',
        'bin/fix_fmt.py',
        'bin/keep_fld.py',
        'bin/marc_check.py',
        'bin/marc_count.py',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python'
    ],
    requires=requirements
)
