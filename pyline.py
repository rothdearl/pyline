#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
from typing import final, Final, List


@final
class Globals:
    """
    Class for managing global constants and instances across the entire application.
    """
    COLOR_FILE_NAME: Final[str] = "\033[0;36m"  # Cyan
    COLOR_LINE_NUMBER: Final[str] = "\033[0;93m"  # High intensity yellow
    COLOR_MATCH: Final[str] = "\033[0;91m"  # High intensity red
    COLOR_RESET: Final[str] = "\033[0m"
    LINES_TO_PRINT: Final[List[str]] = []
    options: argparse.Namespace
    repeated_blank_lines: int
    STDIN_IS_PIPE: Final[bool] = not os.isatty(sys.stdin.fileno())
    STDOUT_IS_PIPE: Final[bool] = not os.isatty(sys.stdout.fileno())
    TAB: Final[str] = ">··"
    VERSION: Final[str] = "1.9.2"


def highlight_matches(patterns: List[str], line: str) -> str:
    """
    Highlights all patterns in the line.
    :param patterns: The patterns.
    :param line: The line to check.
    :return: The line with matches highlighted.
    """
    flags = re.IGNORECASE if Globals.options.ignore_case else 0

    for pattern in patterns:
        if match := re.search(pattern, line, flags=flags):
            replace = line[match.start():match.end()]
            line = line.replace(replace, f"{Globals.COLOR_MATCH}{replace}{Globals.COLOR_RESET}")

    return line


def line_has_find_match(patterns: List[str], line: str) -> bool:
    """
    Returns True if any of the find patterns are found in the line.
    :param patterns: The patterns.
    :param line: The line to check.
    :return: True or False.
    """
    has_match = False
    flags = re.IGNORECASE if Globals.options.ignore_case else 0
    pattern = None

    try:
        for pattern in patterns:
            if re.search(pattern, line, flags=flags):
                has_match = True
                break
    except re.error:
        print_error_message(f"invalid regex pattern: {pattern}")

    return has_match


def line_has_find_matches(patterns: List[str], line: str) -> bool:
    """
    Returns True if all the find patterns are found in the line.
    :param patterns: The patterns.
    :param line: The line to check.
    :return: True or False.
    """
    has_match = True
    flags = re.IGNORECASE if Globals.options.ignore_case else 0
    pattern = None

    try:
        for pattern in patterns:
            if not re.search(pattern, line, flags=flags):
                has_match = False
                break
    except re.error:
        print_error_message(f"invalid regex pattern: {pattern}")

    return has_match


def main() -> None:
    """
    A program to process lines of input.
    :return: None
    """
    parse_arguments()

    try:
        # If the input is from a pipe, process from stdin. Otherwise, process files from the command line.
        if Globals.STDIN_IS_PIPE:
            if Globals.options.pif:  # Option: --pif
                process_files(sys.stdin)
            else:
                process_lines(sys.stdin)
                print_lines()

            if Globals.options.files:  # Process any additional file parameters.
                process_files(Globals.options.files)
        elif Globals.options.files:
            process_files(Globals.options.files)
    except KeyboardInterrupt:
        pass  # Process interrupted; exit quietly.


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None.
    """
    # Build the argument parser.
    parser = argparse.ArgumentParser(allow_abbrev=False, description="utility for processing lines of input.",
                                     epilog="files after a find, exclude or yank will be treated as patterns")
    line_numbers = parser.add_mutually_exclusive_group()
    search = parser.add_argument_group("search options")

    parser.add_argument("files", help="files to process lines from", metavar="files", nargs="*")
    parser.add_argument("-a", "--add-newline", action="store_true", help="add a newline after processing")
    parser.add_argument("-e", "--escape", action="store_true", help="escape\\ white\\ space")
    parser.add_argument("-i", "--ignore-blank", action="store_true", help="ignore blank lines")
    parser.add_argument("-l", "--trim-leading", action="store_true", help="trim leading whitespace")
    line_numbers.add_argument("-n", "--line-numbers", action="store_true", help="show line numbers")
    line_numbers.add_argument("-o", "--number-lines", action="store_true", help="number printed lines")
    parser.add_argument("-q", "--quiet", action="store_true", help="no file name headers or error messages")
    parser.add_argument("-s", "--squeeze-blank", action="store_true", help="suppress repeated blank lines")
    parser.add_argument("-t", "--trim-trailing", action="store_true", help="trim trailing whitespace")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {Globals.VERSION}")
    parser.add_argument("-w", "--wrap", help="^wrap lines between tokens$", metavar=("^", "$"), nargs=2)
    parser.add_argument("--change-tabs", help="change tabs to 'n' spaces", metavar='n', type=int)
    parser.add_argument("--show-tabs", action="store_true", help=f"show tabs as {Globals.TAB}")
    parser.add_argument("--pif", action="store_true", help="treat piped input as file names")
    parser.add_argument("--iso", action="store_true", help="if --pif, use ISO-8859-1 for encoding instead of UTF-8")
    parser.add_argument("--name-only", action="store_true",
                        help="if --pif, display just the file name when find or exclude patterns are found")

    # Search options.
    search.add_argument("--find", help="find lines that contain any pattern", metavar="pattern", nargs="+")
    search.add_argument("--find-all", help="find lines that contain all patterns", metavar="pattern", nargs="+")
    search.add_argument("--exclude", help="exclude lines that contain any pattern", metavar="pattern", nargs="+")
    search.add_argument("--exclude-all", help="exclude lines that contain all patterns", metavar="pattern", nargs="+")
    search.add_argument("--replace", help="replace any pattern", metavar=("pattern", "replace"), nargs=2)
    search.add_argument("--yank", help="yank any pattern from lines", metavar="pattern", nargs="+")
    search.add_argument("--highlight", action="store_true", help="highlight matches in lines")
    search.add_argument("--ignore-case", action="store_true", help="ignore case when pattern matching")

    # Parse the arguments.
    Globals.options = parser.parse_args()


def print_error_message(message: str) -> None:
    """
    Prints an error message and stops processing.
    :param message: The message to print.
    :return: None
    """
    if not Globals.options.quiet:
        print(f"error: {message}", file=sys.stderr)

    raise SystemExit()  # Stop processing.


def print_file_name(file_name: str) -> None:
    """
    Prints the file name.
    :param file_name: The file name.
    :return: None
    """
    if Globals.STDOUT_IS_PIPE:
        print(f"[{file_name}]")
    else:
        left_bracket = f"\033[1m[{Globals.COLOR_RESET}"  # Bold
        right_bracket = f"\033[1m]{Globals.COLOR_RESET}"  # Bold

        print(f"{left_bracket}{Globals.COLOR_FILE_NAME}{file_name}{Globals.COLOR_RESET}{right_bracket}")


def print_lines() -> None:
    """
    Prints the lines.
    :return: None
    """
    for line in Globals.LINES_TO_PRINT:
        print(line)


def process_files(files) -> None:
    """
    Processes the lines from the files.
    :param files: The files to process lines from.
    :return: None
    """
    encoding = "ISO-8859-1" if Globals.options.iso else "UTF-8"

    for file in files:
        file = remove_newline(file)

        try:
            if os.path.isdir(file):
                process_lines(os.listdir(file))
            else:
                with open(file, "r", encoding=encoding) as lines:
                    process_lines(lines.readlines())

            if Globals.LINES_TO_PRINT:
                # The "name_only" option is only when a find or exclude was provided.
                if Globals.options.name_only and (Globals.options.find or Globals.options.exclude):
                    print(file)
                else:
                    if not Globals.options.quiet:
                        print_file_name(file)

                    print_lines()
        except FileNotFoundError:
            print_error_message(f"no such file or directory: {file}")
        except UnicodeDecodeError:
            print(f"unable to decode file: {file}")


def process_line_with_options(line: str, line_number: int) -> bool:
    """
    Processes the line according to the options.
    :param line: The line to print.
    :param line_number: The current line number.
    :return: Whether the line was added to the lines to print.
    """
    can_print = True

    # Option: --find-all
    if Globals.options.find_all:
        can_print = line_has_find_matches(Globals.options.find_all, line)

    # Option: --find
    if can_print and not Globals.options.find_all and Globals.options.find:
        can_print = line_has_find_match(Globals.options.find, line)

    # Option: --exclude-all
    if can_print and Globals.options.exclude_all:
        can_print = not line_has_find_match(Globals.options.exclude_all, line)

    # Option: --exclude
    if can_print and not Globals.options.exclude_all and Globals.options.exclude:
        can_print = not line_has_find_match(Globals.options.exclude, line)

    # Option: --ignore-blank and --squeeze-blank
    if can_print and not line:
        Globals.repeated_blank_lines += 1

        if Globals.options.ignore_blank:
            can_print = False
        elif Globals.options.squeeze_blank and Globals.repeated_blank_lines > 1:
            can_print = False
    else:
        Globals.repeated_blank_lines = 0

    if can_print:
        # Option: --yank
        if Globals.options.yank:
            line = replace_from_line(Globals.options.yank, str(), line)

        # Option: --replace
        if Globals.options.replace:
            line = replace_from_line(Globals.options.replace[0:1], Globals.options.replace[1], line)

        # Option: --change-tabs
        if Globals.options.change_tabs:
            line = line.expandtabs(Globals.options.change_tabs)

        # Option: --highlight
        if Globals.options.highlight and not Globals.STDOUT_IS_PIPE:
            if Globals.options.find_all:
                line = highlight_matches(Globals.options.find_all, line)
            elif Globals.options.find:
                line = highlight_matches(Globals.options.find, line)

        # Option: --show-tabs
        if Globals.options.show_tabs:
            line = line.replace("\t", f"{Globals.TAB}")

        # Option: --escape
        if Globals.options.escape:
            line = line.replace(" ", "\\ ")

        # Option: --trim-leading and --trim-trailing
        line = trim_line(line)

        # Option: --wrap
        wrap_first = str()
        wrap_last = str()

        if Globals.options.wrap:
            wrap_first = Globals.options.wrap[0]
            wrap_last = Globals.options.wrap[1]

        # Option: --line-numbers and --number-lines
        if Globals.options.line_numbers or Globals.options.number_lines:
            if Globals.STDOUT_IS_PIPE:
                Globals.LINES_TO_PRINT.append(f"{line_number:>4}: {wrap_first}{line}{wrap_last}")
            else:
                Globals.LINES_TO_PRINT.append(
                    f"{Globals.COLOR_LINE_NUMBER}{line_number:>4}:{Globals.COLOR_RESET} {wrap_first}{line}{wrap_last}")
        else:
            Globals.LINES_TO_PRINT.append(f"{wrap_first}{line}{wrap_last}")

    return can_print


def process_lines(lines) -> None:
    """
    Processes the lines.
    :param lines: The lines to process.
    :return: None
    """
    lined_added: bool
    line_number = 1

    # Clear any previous line processing.
    Globals.LINES_TO_PRINT.clear()
    Globals.repeated_blank_lines = 0

    for line in lines:
        lined_added = process_line_with_options(remove_newline(line), line_number)

        # Increment the line number if a line was added or the line_numbers option was specified.
        if lined_added or Globals.options.line_numbers:
            line_number += 1

    # Option: --add-newline
    if Globals.LINES_TO_PRINT and Globals.options.add_newline:
        Globals.LINES_TO_PRINT.append(str())


def remove_newline(string: str) -> str:
    """
    Removes the newline character from the end of the string.
    :param string: The string to remove the newline from.
    :return: The string without a newline.
    """
    return string[:-1] if string[-1] == "\n" else string


def replace_from_line(patterns: List[str], replacement: str, line: str) -> str:
    """
    Replaces patterns from the line.
    :param patterns: The patterns to replace.
    :param replacement: The replacement.
    :param line: The line to replace from.
    :return: The line.
    """
    flags = re.IGNORECASE if Globals.options.ignore_case else 0
    pattern = None

    try:
        for pattern in patterns:
            line = re.sub(pattern, replacement, line, flags=flags)
    except re.error:
        print_error_message(f"invalid regex pattern: {pattern}")

    return line


def trim_line(line: str) -> str:
    """
    Trims the line according to the options.
    :param line: The line to trim.
    :return: The line trimmed.
    """
    trim_chars = " \t\v"

    if Globals.options.trim_leading:
        line = line.lstrip(trim_chars)

    if Globals.options.trim_trailing:
        line = line.rstrip(trim_chars)

    return line


if __name__ == "__main__":
    main()
