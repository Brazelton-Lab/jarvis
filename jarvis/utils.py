#! /usr/bin/env python

"""
Contains various functions for use by jarvis.py
"""

import argparse

__author__ = 'Alex Hyer, Christopher Thornton'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Alpha'
__version__ = '2.0.0a1'


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

    def __call__(self, parser, namespace, value, option_string=None):
        """Called by Argparse when user specifies a comma-separated list

        Simply split list by commas and add to namespace.

        Args:

            parser (ArgumentParser): parser used to generate values

            namespace (Namespace): namespace to set values for

            value (str): actual value specified by user

            option_string (str): argument flag used to call this function

        Raises:

            TypeError: if values is not a string

            ValueError: if value cannot, for any reason, be parsed
                        by commas
        """

        # This try/except should already be taken care of by Argparse
        try:
            assert type(value) is str
        except AssertionError:
            raise TypeError('{0} is not a string'.format(value))

        try:
            arguments = filter(None, value.split(','))
        except AssertionError:
            raise ValueError('{0} could not be parsed by commas'
                             .format(value))

        setattr(namespace, self.dest, arguments)
