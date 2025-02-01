#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
from typing import Final, final


@final
class Globals:
    """
    Class for managing global constants and instances across the entire application.
    """
    COLOR_FILE_NAME: Final[str] = "\033[0;96m"  # High intensity cyan
    COLOR_LINE_NUMBER: Final[str] = "\033[0;93m"  # High intensity yellow
    COLOR_MATCH: Final[str] = "\033[0;91m"  # High intensity red
    COLOR_RESET: Final[str] = "\033[0m"
    count_matches_sum: int
    LINES_TO_PRINT: Final[list[str]] = []
    options: argparse.Namespace
    OS_IS_WINDOWS: Final[bool] = os.name == 'nt'
    repeated_blank_lines: int
    STDIN_IS_PIPE: Final[bool] = not os.isatty(sys.stdin.fileno())
    STDOUT_IS_PIPE: Final[bool] = not os.isatty(sys.stdout.fileno())
    TAB: Final[str] = ">··" if OS_IS_WINDOWS else "➡"
    VERSION: Final[str] = "1.10.6"


def count_matches(patterns: list[str], line: str) -> int:
    """
    Returns the number of times the patterns are found in the line.
    :param patterns: The patterns.
    :param line: The line.
    :return: The number of times the patterns are found in the line.
    """
    count = 0
    flags = re.IGNORECASE if Globals.options.ignore_case else 0

    for pattern in patterns:
        if matches := re.findall(pattern, line, flags=flags):
            count += len(matches)

    return count


def highlight_matches(patterns: list[str], line: str) -> str:
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


def line_has_find_match(patterns: list[str], line: str) -> bool:
    """
    Returns true if any of the find patterns are found in the line.
    :param patterns: The patterns.
    :param line: The line to check.
    :return: True or false.
    """
    flags = re.IGNORECASE if Globals.options.ignore_case else 0
    has_match = False
    pattern = None

    try:
        for pattern in patterns:
            if re.search(pattern, line, flags=flags):
                has_match = True
                break
    except re.error:
        print_error_message(f"invalid regex pattern: {pattern}")

    return has_match


def line_has_find_matches(patterns: list[str], line: str) -> bool:
    """
    Returns true if all the find patterns are found in the line.
    :param patterns: The patterns.
    :param line: The line to check.
    :return: True or false.
    """
    flags = re.IGNORECASE if Globals.options.ignore_case else 0
    has_match = True
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
    else:
        print_error_message("no input files", stop_processing=False)


def parse_arguments() -> None:
    """
    Parses the command line arguments to get the program options.
    :return: None
    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description="utility for processing lines of input",
                                     epilog="files after a find, exclude or yank will be treated as patterns")
    line_numbers = parser.add_mutually_exclusive_group()

    parser.add_argument("files", help="files to process lines from", metavar="files", nargs="*")
    parser.add_argument("-a", "--add-newline", action="store_true", help="add a newline after processing")
    parser.add_argument("-b", "--ignore-blank", action="store_true", help="ignore blank lines")
    parser.add_argument("-e", "--escape", action="store_true", help="escape\\ white\\ space")
    parser.add_argument("-l", "--trim-leading", action="store_true", help="trim leading whitespace")
    line_numbers.add_argument("-n", "--line-numbers", action="store_true", help="show line numbers")
    line_numbers.add_argument("-o", "--number-output", action="store_true", help="number output lines")
    parser.add_argument("-q", "--quiet", action="store_true", help="no file name headers or error messages")
    parser.add_argument("-s", "--squeeze-blank", action="store_true", help="suppress repeated blank lines")
    parser.add_argument("-t", "--trim-trailing", action="store_true", help="trim trailing whitespace")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {Globals.VERSION}")
    parser.add_argument("-w", "--wrap", help="^wrap lines between tokens$", metavar=("^", "$"), nargs=2)
    parser.add_argument("--change-tabs", help="change tabs to 'n' spaces", metavar='n', type=int)
    parser.add_argument("-T", "--show-tabs", action="store_true", help=f"show tabs as {Globals.TAB}")
    parser.add_argument("--pif", action="store_true", help="treat piped input as file names")
    parser.add_argument("--iso", action="store_true", help="if --pif, use ISO-8859-1 for encoding instead of UTF-8")
    parser.add_argument("-N", "--name", action="store_true",
                        help="if --pif, show just the file name for find or exclude patterns")

    # Search options.
    search = parser.add_argument_group("search options")
    find = search.add_mutually_exclusive_group()
    exclude = search.add_mutually_exclusive_group()
    count = search.add_mutually_exclusive_group()

    find.add_argument("-f", "--find", help="find lines that contain any pattern", metavar="pattern", nargs="+")
    find.add_argument("-F", "--find-all", help="find lines that contain all patterns", metavar="pattern", nargs="+")
    exclude.add_argument("-x", "--exclude", help="exclude lines that contain any pattern", metavar="pattern", nargs="+")
    exclude.add_argument("-X", "--exclude-all", help="exclude lines that contain all patterns", metavar="pattern",
                         nargs="+")
    search.add_argument("-r", "--replace", help="replace any pattern", metavar=("pattern", "replace"), nargs=2)
    search.add_argument("-y", "--yank", help="yank any pattern from lines", metavar="pattern", nargs="+")
    search.add_argument("-H", "--highlight", action="store_true", help="highlight matches in lines")
    search.add_argument("-i", "--ignore-case", action="store_true", help="ignore case when pattern matching")
    count.add_argument("-c", "--count", action="store_true", help="show just the count for find patterns")
    count.add_argument("-S", "--sum", action="store_true", help="show just the sum for find patterns")

    # Parse the arguments.
    Globals.options = parser.parse_args()


def print_error_message(message: str, *, stop_processing: bool = True) -> None:
    """
    Prints an error message.
    :param message: The message to print.
    :param stop_processing: Whether to stop processing; default is true.
    :return: None
    """
    if not Globals.options.quiet:
        if Globals.STDOUT_IS_PIPE:
            print(f"error: {message}", file=sys.stderr)
        else:
            print(f"{Globals.COLOR_MATCH}error{Globals.COLOR_RESET}: {message}", file=sys.stderr)

    if stop_processing:
        raise SystemExit()


def print_file_name(file_name: str) -> None:
    """
    Prints the file name.
    :param file_name: The file name.
    :return: None
    """
    if Globals.STDOUT_IS_PIPE:
        print(f"[{file_name}]")
    else:
        italics = "\u001b[3m"

        if Globals.OS_IS_WINDOWS:
            bold = "\033[1m"
            left_bracket = f"{bold}[{Globals.COLOR_RESET}"
            right_bracket = f"{bold}]{Globals.COLOR_RESET}"

            print(f"{left_bracket}{Globals.COLOR_FILE_NAME}{italics}{file_name}{Globals.COLOR_RESET}{right_bracket}")
        else:
            emoji = "📁" if os.path.isdir(file_name) else "📄"

            print(f"{emoji:2}{Globals.COLOR_FILE_NAME}{italics}{file_name}{Globals.COLOR_RESET}")


def print_lines() -> None:
    """
    Prints the lines.
    :return: None
    """
    if Globals.options.sum:
        print(Globals.count_matches_sum)
    else:
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
                # The "--name" option is only when a find or exclude was provided.
                if Globals.options.name and (Globals.options.find or Globals.options.exclude):
                    print(file)
                else:
                    if not Globals.options.quiet:
                        print_file_name(file)

                    print_lines()
        except FileNotFoundError:
            print_error_message(f"no such file or directory: {file}", stop_processing=False)
        except PermissionError:
            print_error_message(f"operation not permitted for: {file}", stop_processing=False)
        except UnicodeDecodeError:
            print_error_message(f"unable to decode file: {file}", stop_processing=False)


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

        # Option: --count or --sum
        if can_print and (Globals.options.count or Globals.options.sum):
            count = count_matches(Globals.options.find_all, line)
            Globals.count_matches_sum += count
            line = str(count)

    # Option: --find
    if can_print and Globals.options.find:
        can_print = line_has_find_match(Globals.options.find, line)

        # Option: --count or --sum
        if can_print and (Globals.options.count or Globals.options.sum):
            count = count_matches(Globals.options.find, line)
            Globals.count_matches_sum += count
            line = str(count)

    # Option: --exclude-all
    if can_print and Globals.options.exclude_all:
        can_print = not line_has_find_match(Globals.options.exclude_all, line)

    # Option: --exclude
    if can_print and Globals.options.exclude:
        can_print = not line_has_find_match(Globals.options.exclude, line)

    # Option: --ignore-blank or --squeeze-blank
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
            line = line.replace("\t", f"{Globals.TAB:2}")

        # Option: --escape
        if Globals.options.escape:
            line = line.replace(" ", "\\ ")

        # Option: --trim-leading or --trim-trailing
        line = trim_line(line)

        # Option: --wrap
        wrap_first = str()
        wrap_last = str()

        if Globals.options.wrap:
            wrap_first = Globals.options.wrap[0]
            wrap_last = Globals.options.wrap[1]

        # Option: --line-numbers or --number-output
        if Globals.options.line_numbers or Globals.options.number_output:
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
    Globals.count_matches_sum = 0
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


def replace_from_line(patterns: list[str], replacement: str, line: str) -> str:
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
    try:
        # Fix ANSI escape sequences on Windows.
        if Globals.OS_IS_WINDOWS:
            from colorama import just_fix_windows_console

            just_fix_windows_console()

        # Prevent a broken pipe error (not supported on Windows).
        if not Globals.OS_IS_WINDOWS:
            from signal import SIG_DFL, SIGPIPE, signal

            signal(SIGPIPE, SIG_DFL)

        main()
    except KeyboardInterrupt:
        pass  # Process interrupted; exit quietly.
