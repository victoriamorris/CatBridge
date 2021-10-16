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

### get_fields

*get_fields* is a utility which extracts nominated fields and subfields from a file of MARC 21 records.

The fields and subfields to be extracted are specified in a config file.

    Usage: get_fields -i <input_file> -o <output_file> -c <config_file> [options]
    
    Options:
        --trim  Trim subfields & normalize whitespace
        --isbn  Validate and normalize ISBNs and other control numbers
        --rid	Include record ID as the first column of the output file
        --delim=<delim> Specify the delimiter to be used to separate multiple subfields
                        If not specified, default is a single white space

        --debug	Debug mode.
        --help	Show help message and exit.

#### Files

<input_file> is the name of the input file, which must be a file of MARC 21 records.

<output_file> is the name of the file to which the fields/subfields will be written. This should be a text file.

<config_file> is the name of the file containing the configuration directives.

#### The config file

The format of the configuration file is as follows, with one entry per line

    FIELD TAG $ subfield characters

Each line must match the regular expression

    [0-9A-Z]{3}\$?[a-z0-9]*

The field tag is specified using three numbers or UPPERCASE letters.

The subfield codes are specified using one or more numbers or lowercase letters.

If '$' appears *without* any following subfield characters, *all* subfields will be extracted.

Multiple fields and subfields may be specified. Fields may be repeated with different combinations of subfields.

Example:

    001
    020$a 
    015$a
    100$abcd
    100$e
    362$

#### Options

##### --isbn

If option --isbn is used, the contents of the following subfields will be tested to see if they confirm to the 
appropriate pattern. Subfields will be normalized to follow this pattern wherever possible.
- 001 - 9-digit integer, padded with leading 0s
- 010$a - structure specified at https://www.loc.gov/marc/bibliographic/bd010.html; whitespace is preserved
- 015$a, 015$z - any combination of alphanumeric characters, without leading or trailing spaces
- 020$a, 020$z, 021$a, 021$z - a structurally plausible ISBN, with either 10 or 13 digits 
  (where the last digit of a 10-digit ISBN may be the character X); note that the script does not check validity of ISBNs
- 022$a, 022$l, 022$m, 022$y, 022$z - a structurally valid ISSN, consisting of 8 digits from the set [0-9X], 
  separated into two groups of four by a single hyphen 
- 024$a - any combination of alphanumeric characters, without leading or trailing spaces

##### --trim

If option --trim is used, all subfields will be trimmed to remove leading and trailing spaces, 
and whitespace within subfields will be normalized (e.g.. "  " will be replaced by " ").

##### --rid

By default, the output file consists of a single column of strings.
If option --rid is used, the output file will consist of two columns: the first column will be the record control number from field 001
and the second column will be as per the default output.

##### --delim

This option takes an argument. Example:

    get_fields -i input.lex -o output.txt -c config.cfg --delim=--

Whenever multiple subfields of the same field are specified within the config file, 
these will be separated by a delimited when they are written to the output file.
The default delimiter is a single white space (" ").
Option --delim  can be used to specify an alternative delimiter.


