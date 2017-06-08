#! /usr/bin/env python2.7

"""Jerry-rigged Acronym Regarding Versioning Installed Software (jarvis)

Manages a JSON-formatted file containing information on the programs and
reference databases that are available and displays it as human-readable text.
Users can specify a program (or database) of interest as an argument and
receive additional detail about it, including previous versions, dependencies,
and a list of possible commands supplied by the program. Utils also includes
functionality for editing the database.


Copyright:
    jarvis.py  Manages JSON database to store information on installed software
    Copyright (C) 2016  William Brazelton,  Christopher Thornton,  Alex Hyer
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function

import argparse
import json
import os
import sys
import textwrap

__author__ = 'Christopher Thornton, Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Beta'
__version__ = '1.0.0b2'


class ParseCommas(argparse.Action):
    """Argparse Action that parses arguments by commas
    
    Attributes:
        
        option_strings (list): list of str giving command line flags that
                               call this action
                               
        dest (str): Namespace reference to value
        
        nargs (bool): True if multiple arguments specified
        
        **kwargs (various): optional arguments to pass to super call
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize class and spawn self as Base Class w/o nargs
        
        This class will "make" nargs by parsing the commas so it only accepts
        a single string, not a list.
        """

        # Only accept a single value to analyze
        if nargs is not None:
            raise ValueError('nargs not allowed for ParseCommas')

            # Call self again but without nargs

        super(ParseCommas, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Called by Argparse when user specifies multiple threads
        
        Simply asserts that the number of threads requested is greater than 0
        but not greater than the maximum number of threads the computer
        can support.
        
        Args:
            
            parser (ArgumentParser): parser used to generate values
            
            namespace (Namespace): parse_args() generated namespace
            
            values (str): actual value specified by user
            
            option_string (str): argument flag used to call this function
            
        Raises:
            
            TypeError: if values is not a string
            
            ValueError: if threads is less than one or greater than number of
                        threads available on computer
        """

        # This try/except should already be taken care of by Argparse
        try:
            assert type(values) is str
        except AssertionError:
            raise TypeError('{0} is not a string'.format(values))

        try:
            arguments = filter(None, values.split(','))
        except AssertionError:
            raise ValueError('{0} could not be parsed by commas'
                             .format(values))

        setattr(namespace, self.dest, arguments)


def autocomplete(user_prog, data):
    match = False
    matches = []
    for program in data:
        user_prog_lower = user_prog.lower()
        data_prog_lower = program.lower()
        if user_prog_lower == data_prog_lower:
            match = program
            break
        elif data_prog_lower.startswith(user_prog_lower):
            matches.append(program)
    if not match and len(matches) == 1:
        print_out('Assuming "{0}" meant "{1}"'.format(user_prog, matches[0]))
        print()
        match = matches[0]
    elif not match and len(matches) > 1:
        print('Could not unambiguously determine what "{0}" means.'
              .format(user_prog))
        print('Did you mean one of the following:\n{0}'
              .format('\n'.join(matches)))
        sys.exit(0)
    elif not match and len(matches) == 0:
        print('"{0}" did not match anything in the database.'
              .format(user_prog))
        sys.exit(0)
    return match


def display_info(first, second):
    col_two_begin = 20
    indent = ' ' * col_two_begin
    if len(first) > col_two_begin:
        print_out(first)
        print_out(second, initial=indent, subsequent=indent)
    else:
        print_out("{:<20}{}".format(first, second), subsequent=indent)


def relevant_values(all_args, match, data):
    given_args = []
    approved_values = [
        'previous versions',
        'description',
        'version',
        'commands',
        'installation method',
        'dependencies',
        'categories'
    ]
    for arg in all_args:
        if arg in approved_values and all_args[arg]:
            given_args.append(arg)
    return given_args


def sub_display(args, data):
    all_args = vars(args)
    program = autocomplete(args.program, data)
    if program:
        version = data[program]["version"]
        if version:
            col_one = "{}({}): ".format(program, version)
        else:
            col_one = program
        col_two = data[program]["description"]
        display_info(col_one, col_two)
        flags = []
        for arg in all_args:
            if all_args[arg] in data[program]:
                flags.append(all_args[arg])
        for flag in sorted(flags):
            header = flag + ': '
            if isinstance(data[program][flag], list):
                value = ', '.join(sorted(data[program][flag]))
            else:
                value = data[program][flag]
            if value:
                output = value
            else:
                output = 'NA'
            display_info(header, output)
    else:
        output = ("Can not locate \"{}\". Please verify that the program that "
                  "you are searching for is already installed on the server, "
                  "and/or not misspelled, by usings \"utils list\""
                  .format(args.program))
        print_out(output)
        sys.exit(1)


def sub_edit(args, data):
    all_args = vars(args)
    if not args.append:
        match = autocomplete(args.program, data)
    else:
        match = False
    if args.remove:
        if match:
            answer = raw_input("Delete \"{}\" [y, n]? ".format(match))
            if answer.lower() == 'y':
                del data[match]
            elif answer.lower() == 'n':
                sys.exit(0)
            else:
                print("\"{}\" is not a valid option".format(answer))
                sys.exit(1)
        else:
            print_out("\"{}\" does not exists in the database of available "
                      "programs. Nothing done.".format(args.program))
            sys.exit(1)
    elif args.edit:
        if match:
            categories = relevant_values(all_args, match, data)
            for category in categories:
                if isinstance(all_args[category], list) and \
                                all_args[category][0] == '+':
                    all_args[category].remove('+')
                    data[match][category].extend(all_args[category])
                elif isinstance(all_args[category], list) and \
                        all_args[category][0] == '-':
                    data[match][category] = []
                elif isinstance(all_args[category], str) and \
                        all_args[category] == '-':
                    data[match][category] = ''
                else:
                    data[match][category] = all_args[category]
        else:
            print_out("\"{}\" does not exists in database. Nothing to edit."
                      .format(args.program))
    elif args.append:
        if not match:
            data[args.program] = {"description": "", "version": "",
                                  "previous versions": [], "commands": [],
                                  "installation method": "",
                                  "dependencies": [],
                                  "categories": []
                                  }
            categories = relevant_values(all_args, args.program, data)
            for category in categories:
                data[args.program][category] += all_args[category]
        else:
            print_out("\"{}\" already exists in database. Use \"utils edit -e "
                      "<program>\" to modify an entry".format(args.program))
            sys.exit(1)

    utils = io_check(args.database, 'w')
    with open(utils, 'w') as out_h:
        out_h.write(json.dumps(data, sort_keys=True))


def sub_list(args, data):
    """Lists available software from data

        Args:

            args (ArgumentParser): args to control function flow

            data (dict): Dictionary containing available software and
                         metadata about the programs
    """

    def extract_data(software):
        """Extracts information from software for printing

        Formats data from program into two columns for terminal display.
        Note: This function is inside sub_list so it can access data and args.

        Args:

            software (str): string of software to extract data from
        """

        # Add version to output if possible unless brief is True
        version = data[software]['version']
        if args.brief is True:
            col_one = software
        elif version:
            col_one = '{}({}): '.format(software, version)
        else:
            col_one = software

        # Add program description to output unless brief is False
        if args.brief is False:
            col_two = data[software]['description']
        else:
            col_two = ''

        display_info(col_one, col_two)  # Send data for output

    # List available categories
    if args.list_categories:
        categories = []
        for software in sorted(data):
            try:  # Not the fastest algorithm, but not much data here, so eh
                program_categories = data[software]['categories']
                for category in program_categories:
                    if category not in categories:
                        categories.append(category)
            except KeyError:
                pass  # Skip software if it doesn't have a category
        print(os.linesep.join(sorted(categories)))

    # List programs in category
    elif args.categories:
        for category in args.categories:
            print()  # Print format header
            print('-' * 79)
            print('{0}'.format(category).center(79))
            print('-' * 79)
            exists = False  # Track if category found
            for software in sorted(data):
                try:  # Not all software will have a category
                    program_categories = data[software]['categories']
                    if category in program_categories:
                        extract_data(software)
                        exists = True  # At least one software in category
                except KeyError:
                    pass
            if not exists:
                print('No such category: {0}'.format(category))
                print('Type use --list_categories to view possible categories')

    # List all software of no other arguments given
    else:
        for software in sorted(data):
            extract_data(software)


def print_out(line, width=79, initial='', subsequent=''):
    """Convenience function that wraps output before printing it
    
    Args:
        
        line (str): string to print
        
        width (int): number of characters per line in output
        
        initial (str): string to prepend to first line
        
        subsequent (str): string to append to each line after first
        
    Example:
        >>> print_out('print this line', width=15, initial='first ', 
        ... subsequent='not first ')
        first print
        not first this
        not first line
    """
    output = textwrap.fill(line, width, initial_indent=initial,
                           subsequent_indent=subsequent)
    print(output)


def main(args):
    """Main function that runs actual program based on passed args
    
    Args:
    
        args (ArgumentParser): args to control program flow
    """

    args.func(args, json.load(args.database))  # Run function defined by args


def entry():
    """Entry point for console_scripts and called if __name__ == __main__
    
    This function parses the command line and calls main(). main() contains the
    actual program and function calls and entry() acts as an entry for 
    command-line based use and parses arguments. Thus, programs can execute
    jarvis by calling main and passing args via the API.
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=
                                     argparse.RawDescriptionHelpFormatter)

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('program',
                               metavar='PROGRAM',
                               help='entry name')

    db_parser = argparse.ArgumentParser(add_help=False)
    db_parser.add_argument('-b', '--database', metavar="DB",
                           default="/usr/local/etc/utils.json",
                           type=argparse.FileType('rw'),
                           help='use a custom JSON-formatted database file ['
                                'default: /usr/local/etc/utils.json]')

    subparsers = parser.add_subparsers(title='subcommands',
                                       help='exactly one of these commands '
                                            'is required')

    # list-specific arguments
    list_parser = subparsers.add_parser('list',
                                        parents=[db_parser],
                                        help='Display available programs or '
                                             'databases. Default is to list '
                                             'programs only.')
    category_mode = list_parser.add_argument_group('category viewers')
    exclusive_list = category_mode.add_mutually_exclusive_group()
    exclusive_list.add_argument('-c', '--categories',
                                type=str,
                                action=ParseCommas,
                                help='display all entries in the specified '
                                     'categories')
    exclusive_list.add_argument('--list_categories',
                                action='store_true',
                                help='display existing categories')
    category_mode.add_argument('--brief',
                               action='store_true',
                               help='only display program names')
    list_parser.set_defaults(func=sub_list)

    # edit-specific arguments
    edit_parser = subparsers.add_parser('edit',
                                        parents=[parent_parser, db_parser],
                                        help="edit, append, or remove a "
                                             "database entry")
    edit_parser.add_argument('-v', '--version',
                             metavar='VERSION',
                             help='current version of the program (can be '
                                  '"null" if no version '
                                  'info available)')
    edit_parser.add_argument('-s', '--synopsis',
                             dest='description',
                             metavar='DESCRITPTION',
                             help='program description')
    edit_parser.add_argument('-p', '--prev',
                             metavar='VERSION [,VERSION,...]',
                             dest='previous versions',
                             type=str,
                             action=ParseCommas,
                             help='comma-separated list of previous versions '
                                  'with last date used '
                                  '(ex: <version>(to <date>)')
    edit_parser.add_argument('-c', '--commands',
                             metavar='COMMAND [,COMMAND,...]',
                             type=str,
                             action=ParseCommas,
                             help='comma-separated list of commands provided '
                                  'by the program')
    edit_parser.add_argument('-t, --categories',
                             dest='categories',
                             metavar='CATEGORY [,CATEGORY,...]',
                             type=str,action=ParseCommas,
                             help='comma-separated list of categories '
                                  'program is in')
    edit_parser.add_argument('-i', '--installation', metavar='METHOD',
                             dest='installation method',
                             help='method used to install the program')
    edit_parser.add_argument('-d', '--depends',
                             metavar='DEP [,DEP,...]',
                             dest='dependencies',
                             type=str,
                             action=ParseCommas,
                             help='comma-separated list of program '
                                  'dependencies')
    group_mode = edit_parser.add_argument_group('actions')

    exclusive_group = group_mode.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('-a', '--append',
                                 action='store_true',
                                 help='add new entry to database')
    exclusive_group.add_argument('-e', '--edit',
                                 action='store_true',
                                 help='edit existing entry in database')
    exclusive_group.add_argument('-r', '--remove',
                                 action='store_true',
                                 help='remove existing entry from database')
    edit_parser.set_defaults(func=sub_edit)

    # display-specific arguments
    display_parser = subparsers.add_parser('show',
                                           parents=[parent_parser, db_parser],
                                           help='obtain detailed information '
                                                'about a program or database')
    flag_group = display_parser.add_argument_group('flags')
    flag_group.add_argument('-p', '--prev',
                            action='store_const',
                            const='previous versions',
                            help='list former versions of the search item')
    flag_group.add_argument('-c', '--commands',
                            action='store_const',
                            const='commands',
                            help='list available commands provided by program')
    flag_group.add_argument('-t', '--categories',
                            action='store_const',
                            const='categories',
                            help='list of categories the search item fits in')
    flag_group.add_argument('-i', '--installation',
                            action='store_const',
                            const='installation method',
                            help='display method used to install program')
    flag_group.add_argument('-d', '--depends',
                            action='store_const',
                            const='dependencies',
                            help='list program dependencies')
    display_parser.set_defaults(func=sub_display)

    main(parser.parse_args())

    sys.exit(0)

if __name__ == '__main__':
    entry()
