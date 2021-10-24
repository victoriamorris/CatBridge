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
| cn-find | [cn_find](#cn_find) | CN-FIND \<infile> \<outfile> \<configfile> | cn_find -i <input_file> \[\<input_file> ...\] -o <output_file> -c <config_file> |
| cn-tidy | [cn_find](#cn_find) | CN-FIND \<infile> | cn_find -i <input_file> \[\<input_file> ...\] -o <output_file> -c <config_file> --tidy |
| del-fld | [keep_fld](#keep_fld) | DEL-FLD \<infile> \<configfile> | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> --delete |
| del-fld2 | [keep_fld](#keep_fld) | DEL-FLD2 \<infile> \<configfile> | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> --delete |
| keep-fld | [keep_fld](#keep_fld) | KEEP-FLD \<infile> \<configfile> | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> |
| keep-fld2 | [keep_fld](#keep_fld) | KEEP-FLD2 \<infile> \<configfile> | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> |
| marccount | [marc_count](#marc_count) | MARCCOUNT \<infile> \[\<infile>\] | marc_count -i <input_file> \[\<input_file> ...\] |

### Features common to all scripts

#### File formats
Unless otherwise specified, MARC files are in MARC 21 format, with .lex file extensions.
Unless otherwise specified, text files are UTF-8-encoded, with .txt, .csv or .tsv file extensions.
Config files are also text files, but may have the file extension .cfg for convenience.

#### Help
For any script, use the option --help, or run the script without arguments/options, to display help text.

#### Logs and debugging
Logs will be written to catbridge.log within the working directory. 
This is a UTF-8 encoded text field and can be read in any text editor.
The default logging level is INFO; if option --debug is set, the logging level is changed to DEBUG.
See https://docs.python.org/3/library/logging.html#levels for information about logging levels.

#### Command line arguments
Command line arguments may be provided in any order.

#### Control fields
For the purposes of these scripts, a field tag is interpreted as a control field tag if and only if it 
(a) takes a numerical value starting with two zeros, or (b) is either of the Aleph control fields "DB " or "SYS".

### cn_find

*cn_find* is a utility which extracts extract control numbers from specified fields and subfields 
within a file of MARC records.

The fields and subfields to be extracted are specified in a config file.

    Usage: cn_find -i <input_file> [<input_file> ...] -o <output_file> -c <config_file> [options]
    
    Options:
        --conv  Convert 10-digit ISBNs to 13-digit form where possible
        --rid   Include record ID as the first column of the output file
        --tidy  Sort and de-duplicate list

        --debug	Debug mode
        --help	Show help message and exit

#### Files

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    cn_find -i file1.lex file2.lex file3.lex -o output.txt -c config.cfg

Wildcard characters may be used. E.g. 

    cn_find -i file*.lex -o output.txt -c config.cfg

<output_file> is the name of the file to which the control numbers will be written. This should be a text file.

<config_file> is the name of the file containing the configuration directives.

#### The config file

The format of the configuration file is as follows, with one entry per line

    =CONTROL_FIELD_TAG [double space] control_number_specification

    or

    =DATA_FIELD_TAG [double space] indicator_values $subfield_code control_number_specification

Each line must match one of the two regular expressions below.
The first is for control fields, the second is for data fields.

    ^=(00[0-9]|[A-Z]{3})\s*\t(.*?)\s*$

    ^=[0-9A-Z]{3}  [0-9*#][0-9*#]\$[a-z0-9*]\t(.*?)\s*$

Note that for data fields there are *two* spaces between the field tag and the indicators.

The field tag is specified using three digits or UPPERCASE letters.

For data fields, indicators are each specified using a single digit, or the character # to specify a blank indicator.
The wildcard character * may be used to mean *any* indicator value.

For data fields, the subfield code is specified using a single digit or lowercase letter.
Alternatively, $* may be used to mean *all* subfield codes.

The control number specification tells the script what kind of control number to search for within the subfield. 
This can either take a value from a pre-defined list, 
or a regular expression can be used to search for control numbers with any other structure. 
The dollar sign ($) may thus function as either a regular expression metacharacter or a subfield delimiter, 
depending on context. 
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

    =001    BL001
    =015  **$a    BNB
    =020  **$a  ISBN
    =020  ##$z  ISBN10
    =500  ##$a  \b[a-z]{7}\b
    =650  *7$0  FAST


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

### keep_fld

*keep_fld* is a utility to keep or delete specified fields within one or more file(s) of MARC records.

    Usage: keep_fld -i <input_file> [<input_file> ...] -c <config_file> [options]
    
    Options:
        --delete    *Delete* fields specified in <config_file>
        --debug	Debug mode
        --help	Show help message and exit

#### Files

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    keep_fld -i file1.lex file2.lex file3.lex -c config.cfg

Wildcard characters may be used. E.g. 

    keep_fld -i file*.lex -c config.cfg

If option --delete is *not* used, the utility writes output for each input file to a file with the same name, 
but	prefixed with "k-".

If option --delete *is* used, the utility writes output for each input file to a file with the same name, 
but	prefixed with "d-".

#### The config file

The format of the configuration file is as follows, with one entry per line.
This format is chosen to resemble MARCbreaker (MARC screen dump) format.

    =CONTROL_FIELD_TAG [double space] content_specification

    or

    =DATA_FIELD_TAG [double space] indicator_values $subfield_code content_specification

Each line must match one of the two regular expressions below.
The first is for control fields, the second is for data fields.

    ^=(00[0-9]|[A-Z]{3})(  )?(.*?)$

    ^=[0-9A-Z]{3}  [0-9*#][0-9*#]($[a-z0-9*] ?.*?)*$

Note that there are *two* spaces between the field tag and the indicators/control field value.

The field tag is specified using three digits or UPPERCASE letters.

For data fields, indicators are each specified using a single digit, or the character # to specify a blank indicator.
The wildcard character * may be used to mean *any* indicator value.

For data fields, the subfield code is specified using a single digit or lowercase letter.
Alternatively, $* may be used to mean *all* subfield codes.

For data fields, the section <span style="color: purple">$subfield_code content_specification</span> 
may be omitted in order to keep/delete an entire field, or repeated multiple times in order to provide different 
instructions for several subfields.

The content specification tells the script what to search for within the subfield.
This will be interpreted by the utility as a case-sensitive regular expression.
The dollar sign ($) may thus function as either a regular expression metacharacter or a subfield delimiter, 
depending on context. As a subfield delimited, the dollar sign will always be followed by a subfield code;
as a regular expression metacharacter it will either be followed by another dollar sign 
(this one being a subfield delimiter) or will appear at the end of the string.

*Note:* Field 001 will *always* be included in the output file.

##### Examples

To keep/delete field 041:

    =041  **

To keep/delete field 041 subfield $a:
    
    =041  **$a

To keep/delete field 041 whenever the second indicator is blank:
    
    =041  *#

To keep/delete field 041 subfield $a whenever it contains "eng":
    
    =041  **$aeng

To keep/delete field 041 subfield $a whenever it contains a digit 
(remember that the content specification is interpreted as a regular expression):
    
    =041 **$a.*[0-9].*

To keep/delete field 041 subfields $a and $h whenever they are equal to "fre"
(here the dollar sign is being used as a regular expression metacharacter as well as a subfield delimiter):
    
    =041  **$a^fre$$h^fre$

To keep/delete any subfields of field 041 which contain an uppercase letter:
    
    =041  **$*.*[A-Z].*

#### Options

##### --delete

By default, only the fields or subfields specified in the config file will be retained in the output.

If option --delete is used, the specified fields and subfields will instead be deleted from the input file.

### marc_count

*marc_count* is a utility which counts the number of records present within one or more file(s) of MARC records.

    Usage: marc_count -i <input_file> [<input_file> ...] [options]
    
    Options:
        --debug	Debug mode
        --help	Show help message and exit

#### Files

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    marc_count -i file1.lex file2.lex file3.lex

Wildcard characters may be used. E.g. 

    marc_count -i file*.lex

This will count all the files with .lex suffix in the current directory, and output numbers of records per file 
as well as a total for all files.
