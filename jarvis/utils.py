#! /usr/bin/env python

"""
Contains various functions for use by jarvis.py
"""

import argparse
from difflib import get_close_matches

__author__ = 'Alex Hyer, Christopher Thornton'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Alpha'
__version__ = '2.0.0a3'


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


def autocorrect(query, possibilities, delta=0.75):
    """Attempts to figure out what possibility the query is

    Args:
        query (unicode): query to attempt to complete

        possibilities (list): list of unicodes of possible answers for query

        delta (float): minimum delta similarity between query and
                       any given possibility for possibility to be considered.
                       Delta used by difflib.get_close_matches().

    Returns:
        unicode: best guess of correct answer

    Raises:
        AssertionError: raised if no matches found

    Example:
    >>> autocomplete('bowtei', ['bowtie2', 'bot']
    'bowtie2'
    """

    possibilities = [possibility.lower() for possibility in possibilities]

    # Don't waste time for exact matches
    if query in possibilities:
        return query

    # Complete query as much as possible
    options = [word for word in possibilities if word.startswith(query)]
    if len(options) > 0:
        possibilities = options  # possibilities now limited to options
        query = max_substring(options)

    # Identify possible matches and return best match
    matches = get_close_matches(query, possibilities, cutoff=delta)

    try:
        assert len(matches) > 0
    except AssertionError:
        raise AssertionError('No matches for "{0}" found'.format(query))

    return matches[0]


def max_substring(words, last_letter='', position=0):
    """Finds max substring shared by all strings starting at position

    Args:
        words (list): list of unicode of all words to compare

        last_letter (unicode): letter of last common letter, only for use
                               internally unless you really know what
                               you are doing

        position (int): starting position in each word to begin analyzing
                        for substring

    Returns:
        unicode: max string common to all words

    Examples:
    >>> max_substring(['aaaa', 'aaab', 'aaac'])
    'aaa'
    >>> max_substring(['abbb', 'bbbb', 'cbbb'], position=1)
    'bbb'
    >>> max_substring(['abc', 'bcd', 'cde'])
    ''
    """

    # If end of word is reached, begin reconstructing the substring
    try:
        letter = [word[position] for word in words]
    except IndexError:
        return last_letter

    # Recurse if position matches, else begin reconstructing the substring
    if all(l == letter[0] for l in letter) is True:
        last_letter += max_substring(words, last_letter=letter[0],
                                     position=position + 1)
        return last_letter
    else:
        return last_letter
