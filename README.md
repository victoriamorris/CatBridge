# catbridge_tools
Tools for working with MARC data in Catalogue Bridge. 

Borrows heavily from PyMarc (https://pypi.org/project/pymarc/).

## Requirements

Requires the regex module from https://bitbucket.org/mrabarnett/mrab-regex. The built-in re module is not sufficient.

Also requires py2exe.

## Installation

From GitHub:

    git clone https://github.com/victoriamorris/catbridge_tools
    cd catbridge_tools

To install as a Python package:

    python setup.py install
    
To create stand-alone executable (.exe) files for individual scripts:

    python setup.py py2exe 
    
Executable files will be created in the folder \dist, and should be copied to an executable path.

Both of the above commands can be carried out by running the shell script:

    compile_catbridge_tools.sh

## Scripts

The scripts listed below can be run from anywhere, once the package is installed 
and the .exe files have been copied to an executable path.

### Correspondence with original Catalogue Bridge tools

| Original Catalogue Bridge tool | New tool | Original syntax | Corresponding new syntax |
| -------- | -------- | -------- | -------- |
| cn-find | [cn-find](#cn_find) | CN-FIND \<infile> \<outfile> \<configfile> | cn_find -i <input_file> -o <output_file> -c <config_file> |

### Features common to all scripts

#### File formats
Unless otherwise specified, MARC files are in MARC 21 format, with .lex file extensions.
Unless otherwise specified, text files are UTF-8-encoded, with .txt, .csv or .tsv file extensions.
Config files are also text files, but may have the file extension .cfg for convenience.

#### Help
For any script, use the option --help to display help text.

#### Logs and debugging
Logs will be written to catbridge.log within the working directory. 
This is a UTF-8 encoded text field and can be read in any text editor.
The default logging level is INFO; if option --debug is set, the logging level is changed to DEBUG.
See https://docs.python.org/3/library/logging.html#levels for information about logging levels.

### cn_find

*cn_find* is a utility which extracts extract control numbers from specified fields and subfields within a file of MARC records.

The fields and subfields to be extracted are specified in a config file.

    Usage: cn_find -i <input_file> -o <output_file> -c <config_file> [options]
    
    Options:
        --conv  Convert 10-digit ISBNs to 13-digit form where possible
        --rid	Include record ID as the first column of the output file
        --tidy  Sort and de-duplicate list

        --debug	Debug mode.
        --help	Show help message and exit.

#### Files

<input_file> is the name of the input file, which must be a file of MARC 21 records.

<output_file> is the name of the file to which the control numbers will be written. This should be a text file.

<config_file> is the name of the file containing the configuration directives.

#### The config file

The format of the configuration file is as follows, with one entry per line

    FIELD TAG $ subfield character [tab] control number specification

Each line must match the regular expression

    ^([0-9A-Z]{3})\s*\$?\s*([a-z0-9]?)\s*\t(.*?)\s*$

The field tag is specified using three numbers or UPPERCASE letters.

The subfield code are specified using a single number or lowercase letter.
If '$' appears *without* any following subfield characters,  *all* subfields will be searched for control numbers.

The control number specification tells the script what kind of control number to search for within the subfield. 
This can either take a value from a pre-defined list, 
or a regular expression can be used to search for control numbers with any other structure.
Regular expressions are *case-sensitive*.

| Control number specification | Description | Regular expression |
| -------- | ----------- | ----------- |
| ISBN    | Any structurally plausible ISBN* | \b(?=(?:[0-9]+[\- ]?){10})[0-9]{9}[0-9Xx]\b&#124;\b(?=(?:[0-9]+[\- ]?){13})[0-9]{1,5}[\- ][0-9]+[\- ][0-9]+[\- ][0-9Xx]\b&#124;\b97[89][0-9]{10}\b&#124;\b(?=(?:[0-9]+[\- ]){4})97[89][\- 0-9]{13}[0-9]\b |
| ISBN10  | Any structurally plausible 10-digit ISBN* | \b(?=(?:[0-9]+[\- ]?){10})[0-9]{9}[0-9Xx]\b&#124;\b(?=(?:[0-9]+[\- ]?){13})[0-9]{1,5}[\- ][0-9]+[\- ][0-9]+[\- ][0-9Xx]\b |
| ISBN13  | Any structurally plausible 13-digit ISBN* | \b97[89][0-9]{10}\b&#124;\b(?=(?:[0-9]+[\- ]){4})97[89][\- 0-9]{13}[0-9]\b |
| ISSN    | 8 digits with a hyphen in the middle, where the last digit may be an X | \b[0-9]{4}[ \-]?[0-9]{3}[0-9Xx]\b |
| BL001   | 9 digits | \b[0-9]{9}\b |
| BNB     | See https://www.bl.uk/collection-metadata/metadata-services/structure-of-the-bnb-number | \bGB([0-9]{7}&#124;[A-Z][0-9][A-Z0-9][0-9]{4})\b |
| LCCN    | See https://www.loc.gov/marc/bibliographic/bd010.html | \b[a-z][a-z ][a-z ]?[0-9]{2}[0-9]{6} ?\b |
| OCLC    | "(OCoLC)" followed by digits | \(OCoLC\)[0-9]+\b |
| ISNI    | 16 digits separated into groups of 4 with spaces or hyphens | \b[0]{4}[ \-]?[0-9]{4}[ \-]?[0-9]{4}[ \-]?[0-9]{3}[0-9Xx]\b |
| FAST    | "fst" followed by digits | \bfst[0-9]{8}\b |

*Note: The ISBN check digit is *not* validated.

Multiple fields and subfields may be specified. Fields may be repeated with different subfields.

Example:

    001 BL001
    015$a	BNB
    020	ISBN
    020$z	ISBN10
    500$a	\b[a-z]{7}\b
    035$a	OCLC

In the example above, field 500 subfield $a is being searched for 7-character words.

#### Options

##### --conv

If option --conv is used, 10-digit ISBNs will be converted to 13-digit form whenever possible
(i.e. whenever they are valid ISBNs).

##### --rid

By default, the output file consists of a single column of strings.
If option --rid is used, the output file will consist of two columns: the first column will be the record control number 
from field 001 and the second column will be as per the default output.

##### --tidy

If option --tidy is used, the list of control numbers in the output file will be sorted and de-duplicated.
Any duplicate control numbers will be written to an additional output file named with the prefix "dp-".

Note: option --tidy cannot be used at the same time as option --rid
