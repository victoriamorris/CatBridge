# catbridge_tools <a id="catbridge_tools"/>
Tools for working with MARC data in Catalogue Bridge. 

![CatBridge logo](https://github.com/victoriamorris/CatBridge/blob/main/catbridge.png)

Borrows heavily from PyMarc (https://pypi.org/project/pymarc/).

[[back to top]](#catbridge_tools)

## Requirements

Requires the regex module from https://bitbucket.org/mrabarnett/mrab-regex. The built-in re module is not sufficient.=

[[back to top]](#catbridge_tools)

## Installation

From GitHub:
    
```shell
python -m pip install git+https://github.com/victoriamorris/CatBridge.git@main
```

To create stand-alone executable (.exe) files for individual scripts from downloaded source code:

```python
python -m PyInstaller bin/<script_name>.py -F
```

Executable files will be created in the folder \dist, and should be copied to an executable path.

Both of the above commands can be carried out by running the shell script:

```shell
compile_catbridge_tools.sh
```
    
[[back to top]](#catbridge_tools)  

## Scripts

The scripts listed below can be run from anywhere, once the package is installed 
and the .exe files have been copied to an executable path.

### Correspondence with original Catalogue Bridge tools

| Original Catalogue Bridge tool | New tool                   | Original syntax                            | Corresponding new syntax                                                               |
|--------------------------------|----------------------------|--------------------------------------------|----------------------------------------------------------------------------------------|
| cn-find                        | [cn_find](#cn_find)        | CN-FIND \<infile> \<outfile> \<configfile> | cn_find -i <input_file> \[\<input_file> ...\] -o <output_file> -c <config_file>        |
| cn-tidy                        | [cn_find](#cn_find)        | CN-FIND \<infile>                          | cn_find -i <input_file> \[\<input_file> ...\] -o <output_file> -c <config_file> --tidy |
| del-fld                        | [keep_fld](#keep_fld)      | DEL-FLD \<infile> \<configfile>            | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> --delete               |
| del-fld2                       | [keep_fld](#keep_fld)      | DEL-FLD2 \<infile> \<configfile>           | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file> --delete               |
| fix-fmt                        | [fix_fmt](#fix_fmt)        | FIX-FMT \<marcfile>                        | fix_fmt -i <input_file> \[\<input_file> ...\]                                          |
| keep-fld                       | [keep_fld](#keep_fld)      | KEEP-FLD \<infile> \<configfile>           | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file>                        |
| keep-fld2                      | [keep_fld](#keep_fld)      | KEEP-FLD2 \<infile> \<configfile>          | keep_fld -i <input_file> \[\<input_file> ...\] -c <config_file>                        |
| marc-chk                       | [marc_check](#marc_check)  | MARC-CHK \<infile>                         | marc_check -i <input_file> \[\<input_file> ...\]                                       |
| marccount                      | [marc_count](#marc_count)  | MARCCOUNT \<infile> \[\<infile>\]          | marc_count -i <input_file> \[\<input_file> ...\]                                       |


[[back to top]](#catbridge_tools)

### Features common to all scripts

#### Section contents
- [File formats](#formats)
- [Help](#help)
- [Logs and debugging](#logs)
- [Command line arguments](#cla)
- [Control fields](#control_fields)
- [Malformed records/fields](#malformed_records)

#### File formats <a id="formats"/>
Unless otherwise specified, MARC files are in MARC 21 format, with .lex file extensions.
Unless otherwise specified, text files are UTF-8-encoded, with .txt, .csv or .tsv file extensions.
Config files are also text files, but may have the file extension .cfg for convenience.

[[back to top]](#catbridge_tools)

#### Help <a id="help"/>
For any script, use the option --help, or run the script without arguments/options, to display help text.

[[back to top]](#catbridge_tools)

#### Logs and debugging <a id="logs"/>
Logs will be written to catbridge.log within the working directory. 
This is a UTF-8 encoded text field and can be read in any text editor.
The default logging level is INFO; if option --debug is set, the logging level is changed to DEBUG.
See https://docs.python.org/3/library/logging.html#levels for information about logging levels.

[[back to top]](#catbridge_tools)

#### Command line arguments <a id="cla"/>
Command line arguments may be provided in any order.

[[back to top]](#catbridge_tools)

#### Control fields <a id="control_fields"/>
For the purposes of these scripts, a field tag is interpreted as a control field tag if and only if it 
(a) takes a numerical value starting with two zeros, or (b) is either of the Aleph control fields "DB " or "SYS".

[[back to top]](#catbridge_tools)

#### Malformed records/fields <a id="malformed_records"/>
- Missing indicators are recorded as blank spaces (data fields only)
- Extra indicators are ignored (data fields only)

[[back to top]](#catbridge_tools)

### cn_find

#### Section contents
- [Overview](#cn_find_overview)
- [Files](#cn_find_files)
- [Options](#cn_find_options)

[[back to top of section]](#cn_find)

#### Overview <a id="cn_find_overview"/>

*cn_find* is a utility which extracts control numbers from specified fields and subfields 
within a file of MARC records.

The fields and subfields to be extracted are specified in a config file.

```shell
Usage: cn_find -i <input_file> [<input_file> ...] -o <output_file> -c <config_file> [options]

Options:
    --conv  Convert 10-digit ISBNs to 13-digit form where possible
    --rid   Include record ID as the first column of the output file
    --tidy  Sort and de-duplicate list

    --debug	Debug mode
    --help	Show help message and exit
```        

[[back to top of section]](#cn_find)

#### Files <a id="cn_find_files"/>

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    cn_find -i file1.lex file2.lex file3.lex -o output.txt -c config.cfg

Wildcard characters may be used. E.g. 

    cn_find -i file*.lex -o output.txt -c config.cfg

<output_file> is the name of the file to which the control numbers will be written. This should be a text file.

<config_file> is the name of the file containing the configuration directives.

[[back to top of section]](#cn_find)

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

[[back to top of section]](#cn_find)

#### Options <a id="cn_find_options"/>

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

[[back to top of section]](#cn_find)
[[back to top]](#catbridge_tools)

### fix_fmt

#### Section contents
- [Overview](#fix_fmt_overview)
- [Files](#fix_fmt_files)

[[back to top of section]](#fix_fmt)

#### Overview <a id="fix_fmt_overview"/>

All records exported from Aleph contain a FMT field. 
This is exported from Aleph as a control field, with no indicator values or subfield codes. 
However, to be compliant with ISO 2709, control field tags must commence with 00.

*fix_fmt* is a utility which makes records exported from Aleph ISO 2709-compliant by turning the FMT control field
into a data field with two blank indicators and subfield 'a'. 
Any FMT *data* fields present in the input record will be copied to the output file without modification. 

    Usage: marc_count -i <input_file> [<input_file> ...] [options]
    
    Options:
        --debug	Debug mode
        --help	Show help message and exit

[[back to top of section]](#fix_fmt)

#### Files <a id="fix_fmt_files"/>

<input_file> is the name of the input file, which must be a file of MARC 21 records *as exported from Aleph*.

Multiple input files may be listed. E.g.

    fix_fmt -i file1.lex file2.lex file3.lex

Wildcard characters may be used. E.g. 

    fix_fmt -i file*.lex

The utility writes output for each input file to a file with the same name, but	prefixed with "fix-".

[[back to top of section]](#fix_fmt)
[[back to top]](#catbridge_tools)

### keep_fld

#### Section contents
- [Overview](#keep_fld_overview)
- [Files](#keep_fld_files)
- [Options](#keep_fld_options)

[[back to top of section]](#keep_fld)

#### Overview <a id="keep_fld_overview"/>

*keep_fld* is a utility to keep or delete specified fields within one or more file(s) of MARC records.

    Usage: keep_fld -i <input_file> [<input_file> ...] -c <config_file> [options]
    
    Options:
        --delete    *Delete* fields specified in <config_file>
        --debug	Debug mode
        --help	Show help message and exit

[[back to top of section]](#keep_fld)

#### Files <a id="keep_fld_files"/>

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    keep_fld -i file1.lex file2.lex file3.lex -c config.cfg

Wildcard characters may be used. E.g. 

    keep_fld -i file*.lex -c config.cfg

If option --delete is *not* used, the utility writes output for each input file to a file with the same name, 
but	prefixed with "k-".

If option --delete *is* used, the utility writes output for each input file to a file with the same name, 
but	prefixed with "d-".

[[back to top of section]](#keep_fld)

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

[[back to top of section]](#keep_fld)

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

[[back to top of section]](#keep_fld)

#### Options <a id="keep_fld_options"/>

##### --delete

By default, only the fields or subfields specified in the config file will be retained in the output.

If option --delete is used, the specified fields and subfields will instead be deleted from the input file.

[[back to top of section]](#keep_fld)
[[back to top]](#catbridge_tools)

### marc_check

#### Section contents
- [Overview](#marc_check_overview)
- [Files](#marc_check_files)
- [Test data](#marc_check_test)

[[back to top of section]](#marc_check)

#### Overview <a id="marc_check_overview"/>

*marc_check* is a utility which checks the structural validity of records present within one or more file(s) of MARC records,
and isolates those found to be flawed.

    Usage: marc_check -i <input_file> [<input_file> ...] [options]
    
    Options:
        --debug	Debug mode
        --help	Show help message and exit

[[back to top of section]](#marc_check)

###### Checks

The utility performs the following checks on each MARC record:
1. The record contains data.
2. The record <a href="https://www.loc.gov/marc/bibliographic/bdleader.html">Leader</a> has the correct length, 
namely 24 ascii characters.
3. The record length specified in the <a href="https://www.loc.gov/marc/bibliographic/bdleader.html">Leader</a>, 
positions 00-04, matches the observed length of the record.   
    * This number should consist of five digits, and be equal to the length of the entire record, 
including itself and the record terminator.  
    * The number is right justified and unused positions contain zeros.
    * The record must end with an end-of-record character (hex 1D).
    * The record must not contain an end-of-record character (hex 1D) in any other position.
4. The base address specified in the <a href="https://www.loc.gov/marc/bibliographic/bdleader.html">Leader</a>, 
positions 12-16, does not exceed the size of the record.
    * This number should consist of five digits, and be equal to the first character position of the first variable field in the record. 
    * The number is right justified and unused positions contain zeros.
5. The length of the <a href="https://www.loc.gov/marc/bibliographic/bddirectory.html">Directory</a> is a multiple of 12.
6. The <a href="https://www.loc.gov/marc/bibliographic/bddirectory.html">Directory</a> must be followed by an end-of-field character (hex 1E).
    * The end-of-field character is *not* counted when calculating the length of the directory
7. Each entry in the <a href="https://www.loc.gov/marc/bibliographic/bddirectory.html">Directory</a> corresponds to a single field.
    * This field must end with an end-of-field character (hex 1E).
    * This field must not contain an end-of-field character (hex 1E) in any other position.

[[back to top of section]](#marc_check)

#### Files <a id="marc_check_files"/>

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    marc_check -i file1.lex file2.lex file3.lex

Wildcard characters may be used. E.g. 

    marc_check -i file*.lex

This will check all the files with .lex suffix in the current directory.

For each input file, the utility writes flawed records to a file with a name of the <input_file>_f.lex.
Note that the structural problems with these records mean that it will not normally be possible to view this file in MarcView, MarcEdit, etc.

All records which are found to be structurally valid are written to a file with a name of the <input_file>_ok.lex.

A summary of errors found will be written to the [standard log file](#logs).

#### Test data <a id="marc_check_test"/>

Test data for marc_check is provided in the folder test_data/marc_check. This folder contains two .lex files:
1. test_clean.lex
2. test_with_errors.lex

test_clean.lex contains 556 records, none of which have structural flaws.
Output when marc_check is run on this file should look as follows:

```shell
Checking file test_clean.lex
File test_clean.lex contains 0 flawed records
100% [556 records] processed
```

test_with_errors.lex contains the same 556 records, but with deliberate structural flaws.
Output when marc_check is run on this file should look as follows:

```shell
Checking file test_with_errors.lex
Error at record 2: Record length does not match length specified in first 5 bytes of record: specified length 1880; observed 1877
Error at record 3: Record length does not match length specified in first 5 bytes of record: specified length 1740; observed 1744
Error at record 4: Directory is invalid: length 966 is not a multiple of 12
Error at record 9: Base address exceeds size of record: base address 99589; observed record length 2137
Error at record 15: Directory does not end with end-of-field character (b'\x1e')
Error at record 22: Field 47 with tag CAT does not end with end-of-field character (b'\x1e')
Error at record 23: Field 1 with tag 001 does not end with end-of-field character (b'\x1e')
Error at record 29: Field 9 with tag 245 does not end with end-of-field character (b'\x1e')
Error at record 30: Field 16 with tag 504 contains unexpected end-of-field character (b'\x1e')
File test_with_errors.lex contains 9 flawed records
100% [556 records] processed
```

[[back to top of section]](#marc_check)
[[back to top]](#catbridge_tools)

### marc_count

#### Section contents
- [Overview](#marc_count_overview)
- [Files](#marc_count_files)

[[back to top of section]](#marc_count)

#### Overview <a id="marc_count_overview"/>

*marc_count* is a utility which counts the number of records present within one or more file(s) of MARC records.

    Usage: marc_count -i <input_file> [<input_file> ...] [options]
    
    Options:
        --debug	Debug mode
        --help	Show help message and exit

#### Files <a id="marc_count_files"/>

<input_file> is the name of the input file, which must be a file of MARC 21 records.

Multiple input files may be listed. E.g.

    marc_count -i file1.lex file2.lex file3.lex

Wildcard characters may be used. E.g. 

    marc_count -i file*.lex

This will count all the files with .lex suffix in the current directory, and output numbers of records per file 
as well as a total for all files.

[[back to top of section]](#marc_count)
[[back to top]](#catbridge_tools)
