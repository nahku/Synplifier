# Cutting the [TPTP](http://www.tptp.org) language down to size
This project provides a tool for sub-syntax extraction of the [TPTP Syntax](http://www.tptp.org/TPTP/SyntaxBNF.html).

##Motivation

## Getting Started
### Prerequisites

- Python 3.7.x

#### For GUI version

- beautifulsoup4

- PyQt5

#### For Console version

- argparse

## Run the GUI entry point
```
$ python Main.py
```

## Run the command-line entry point
```
$ python Console.py -h
```

## Usage example

###Control file
The control file specifies the start symbol and which productions should be blocked. A sample control file content is:
```
<TPTP_file>
<annotated_formula>,::=,0,1,2,3,5
<annotations>,::=,0
```
In the first line the start symbol <TPTP_file> is selected.
The following lines specify blocked productions.
The second line specifies the indexes of the productions that should be disabled for the <annotated_formula> production with the ::= rule type.
This production can be seen below. All productions excepts <cnf_annotated> are disabled.
In the <annotations> productions, the ,<source><optional_info> production is disabled.
```
<annotated_formula>    ::= <thf_annotated> | <tff_annotated> | <tcf_annotated> |
                           <fof_annotated> | <cnf_annotated> | <tpi_annotated>
[...]
<annotations>          ::= ,<source><optional_info> | <null>
```
To disable more productions just add new lines containing the nonterminal symbol, the rule type and the indexes of the productions to be blocked.
###Command-line

| **Name**             | **Short form** | **Default** | **Description**                                                                                              |
| :------------------- | :------------- | :---------- | :----------------------------------------------------------------------------------------------------------- |
| \--grammar           | \-g            | None        | <span data-acronym-label="TPTP" data-acronym-form="singular+short">TPTP</span> syntax file path and filename |
| \--control           | \-c            | None        | Control file path and filename                                                                               |
| \--output            | \-o            | output.txt  | Output file path and filename (optional)                                                                     |
| \--external\_comment | \-ex           | False       | Flag to include external comment syntax (optional)                                                           |
```
$ python Console.py -g <tptp_syntax_filename>.txt -c <control_file_name>.txt
```
