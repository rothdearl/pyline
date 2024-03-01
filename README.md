## pyline: A Python line processor

**Version:** 1.9.1

### Overview

**pyline** is a simple line processor written in Python. There is nothing **pyline** can do that you can't already do
with `cat`, `grep` and `sed`. **pyline** however, provides a simple interface to finding and editing lines from `stdin`
or from files. **pyline** does not modify the contents of files. It only prints to `stdout` which can be piped to other
commands. **pyline** started out as a simple script to deal with whitespace in file paths from a `find` command in
order to pipe them to `xargs`. From there it grew into a script to perform a variety of functions to lines. The
following document describes its usage.

### Table of Contents

1. [Installation](#Installation)
2. [Whitespace](#Whitespace)
3. [Searching & Filtering](#Searching--Filtering)
4. [PIF](#PIF)
5. [Editing](#Editing)
6. [Misc. Options](#Misc-Options)
7. [Help Output](#Help-Output)
8. [Undocumented Features](#Undocumented-Features)

### Installation

To use **pyline**, download `pyline.py` to a folder in your `PATH` and set the executable flag. Optionally, you can
rename the file to just `pyline` to simplify using it, as it is used in this document. To run pyline, simply run it with
options or use it in a pipe. **pyline** requires `python3` but it can be executed on its own without manually invoking
the interpreter.

### Whitespace

**pyline** can escape, trim or wrap lines to deal with whitespace. This is important when piping output to other
commands that process files. The following examples demonstrate these options, which work the same whether the input is
piped from another command or from a file.

**Examples:**

Escape whitespace:

```bash
find ./ -iname "*.txt" | pyline -e
```

Wrap in double quotes:

```bash
find ./ -iname "*.txt" | pyline --wrap \" \"
```

Wrap in single quotes:

```bash
find ./ -iname "*files*" | pyline --wrap \' \'
```

Trim leading whitespace:

```bash
pyline [file] -l
```

Trim trailing whitespace:

```bash
pyline [file] -t
```

### Searching & Filtering

There are four options for searching for patterns in lines; `--find`, `--find-all`, `--exclude` and `--exclude-all`.
Each option takes an arbitrary list of patterns. `--find` and `--exclude` act like an `or` operator whereas `--find-all`
and `--exclude-all` act like an `and` operator. Additional options are `--ignore-case`, which performs case-insensitive
pattern matching, and `--highlight`, which adds a highlight color to a find match when printed.

**Examples:**

Find all files that end in ".java" and display files names that contain "api" or "util":

```bash
find ./ -iname "*.java" | pyline --find api util
```

Find all files that end in ".java" and display files that contain "api" and "test" regardless of case and highlight the
patterns:

```bash
find ./ -iname "*.java" | pyline --find-all api util --ignore-case --highlight
```

Find all files that end in ".java" and display files names that do not contain "api" and "test" regardless of case:

```bash
find ./ -iname "*.java" | pyline --exclude-all api util --ignore-case
```

### PIF

`--pif` tells **pyline** that the piped input is files. **pyline** will apply the options to the contents of the files
rather than the file names. If a pattern is found using `--pif`, the name of the file will be displayed in a header.
`--name-only` tells **pyline** to display just the file name if a find or exclude pattern is found. This is useful for
deleting files that contain or don't contain a pattern.

**Examples:**

Find all files that end in ".java" and display the lines from the files that contain the text "util":

```bash
find ./ -iname "*.java" | pyline --find util --pif
```

Find all files that end in ".java" and display the file names for files that contain the text "util":

```bash
find ./ -iname "*.java" | pyline --find util --pif --name-only
```

Find all files that end in ".java" and display the file names for files that do not contain the text "util":

```bash
find ./ -iname "*.java" | pyline --exclude util --pif --name-only
```

### Editing

Work in progress...

### Misc. Options

Work in progress...

### Help Output

```bash
pyline -h
```

```
usage: pyline.py [-h] [-a] [-e] [-i] [-l] [-q] [-s] [-t] [-v] [-w ^ $] [--change-tabs n] [--show-tabs] [--pif] [--iso]
                 [--name-only] [--find pattern [pattern ...]] [--find-all pattern [pattern ...]] [--exclude pattern [pattern ...]]
                 [--exclude-all pattern [pattern ...]] [--replace pattern replace] [--yank pattern [pattern ...]]
                 [--highlight] [--ignore-case] [-n | -o] [files ...]

utility for processing lines of input.

positional arguments:
  files                                 files to process lines from

options:
  -h, --help                            show this help message and exit
  -a, --add-newline                     add a newline after processing
  -e, --escape                          escape\ white\ space
  -i, --ignore-blank                    ignore blank lines
  -l, --trim-leading                    trim leading whitespace
  -n, --line-numbers                    show line numbers
  -o, --number-lines                    number printed lines
  -q, --quiet                           no file name headers or error messages
  -s, --squeeze-blank                   suppress repeated blank lines
  -t, --trim-trailing                   trim trailing whitespace
  -v, --version                         show program's version number and exit
  -w ^ $, --wrap ^ $                    ^wrap lines between tokens$
  --change-tabs n                       change tabs to 'n' spaces
  --show-tabs                           show tabs as >··
  --pif                                 treat piped input as file names
  --iso                                 if --pif, use ISO-8859-1 for encoding instead of UTF-8
  --name-only                           if --pif, display just the file name when find or exclude patterns are found

search options:
  --find pattern [pattern ...]          find lines that contain any pattern
  --find-all pattern [pattern ...]      find lines that contain all patterns
  --exclude pattern [pattern ...]       exclude lines that contain any pattern
  --exclude-all pattern [pattern ...]   exclude lines that contain all patterns
  --replace pattern replace             replace any pattern
  --yank pattern [pattern ...]          yank any pattern from lines
  --highlight                           highlight matches in lines
  --ignore-case                         ignore case when pattern matching

files after a find, exclude or yank will be treated as patterns
```

### Undocumented Features

Work in progress...
