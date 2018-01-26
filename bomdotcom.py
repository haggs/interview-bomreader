"""A utility for reading BOM files.

Author:
    Dan Haggerty (daniel.r.haggerty@gmail.com)
Date:
    Jan. 11th, 2018

This module provides a BOMReader class and a command-line tool for reading a
BOM file (text). BOM files contain a value (referred to as n) in the first
line, and a list of parts in the other lines. n is the number of top-n
occurring parts to be listed. Parts can appear in the BOM file in one of three
formats.

BOMReader parses manufacturer, MPN, and the list of reference designators
from each line, and keeps a counter (max heap) of the number of occurrences of
each part.

Usage:
    python bomdotcom.py test_files/example.bom

Example BOM file:
    2
    Wintermute Systems -- CASE-19201:A2,A3
    AXXX-1000:Panasonic:D1,D8,D9
    Z1,Z3;40001;Keystone
    Z1,Z3,Z8;40001;Keystone

Note:
    An MPN can be common across multiple manufacturers, so this file uses the
    term "key" to refer to a unique MPN + manufacturer combination.
"""
import argparse
import collections
import pprint
import re


def parse_line(line):
    """Parses a line from a BOM file and returns a tuple of relevant values.

    Args:
        line: a string containing three values in one of three formats

    Returns:
        A tuple containing manufacturer (str), mpn (str) and a list
        of reference designators (str)
    """
    # Format 1
    if re.match(r'(.*):(.*):(.*)', line):
        split_line = line.split(':')
        mpn = split_line[0]
        manufacturer = split_line[1]
        reference_designators = set(split_line[2].split(','))
    # Format 2
    elif re.match(r'(.*) -- (.*):(.*)', line):
        split_line = line.split(':')
        reference_designators = set(split_line[1].split(','))
        split_line = split_line[0].split('--')
        manufacturer = split_line[0].strip()
        mpn = split_line[1].strip()
    # Format 3
    elif re.match(r'(.*);(.*);(.*)', line):
        split_line = line.split(';')
        reference_designators = set(split_line[0].split(','))
        mpn = split_line[1]
        manufacturer = split_line[2]
    else:
        raise BOMReadError('Error parsing BOM line: {}'.format(line))

    return manufacturer, mpn, reference_designators


class BOMReadError(Exception):
    """Exception for BOM read failures."""
    pass


class BOMNotInstantiatedError(Exception):
    """Exception for when actions are performed on an empty BOMReader."""
    pass


class BOMReader():
    """A BOM file reader class.

    It can read a BOM file, and keep track of the parts listed in it. Provides
    a method for getting a dict of the top-n parts.

    Args:
        input_file_path (str, optional): path to a BOM file to read

    Attributes:
        n (int): the number of top occurring parts to list
        bom (dict): a map of key to part data
        _counter (collections.Counter): a part occurrence counter
    """
    def __init__(self, input_file_path=None):
        self.n = None
        self._bom = None
        self._counter = collections.Counter()

        if input_file_path:
            self.read(input_file_path)

    def read(self, input_file_path):
        """Reads the file specified and populates the internal BOM dict and n.

        Args:
            input_file_path (str): path to the BOM file
        """
        self.n = None
        self._bom = None
        self._counter.clear()

        with open(input_file_path, 'r') as input_file:
            for i, line in enumerate(input_file):
                if i == 0:
                    self.n = int(line)
                else:
                    manufacturer, mpn, ref_des = parse_line(line.strip())
                    self._insert_bom_line(manufacturer, mpn, ref_des)

        if len(self._bom) < self.n:
            raise BOMReadError('The value of n must be less than or equal to'
                               ' the number of BOM lines')

    def get_top_n_parts(self):
        """Get a dict of the top N occurring parts.

        Returns:
            a dict containing the top N parts sorted by number of occurrences,
            then number of reference designators

        Raises:
            BOMNotInstantiatedError: If a BOM file hasn't been read yet
        """
        if self._bom is None:
            raise BOMNotInstantiatedError('No BOM file has been read yet.')

        most_common_keys = [key for key, count in self._counter.most_common()]

        # Sort the keys by parts with the most reference designators (n logn)
        sorted_keys = sorted(most_common_keys, reverse=True,
                             key=lambda k: len(
                                self._bom[k]['ReferenceDesignators']))[:self.n]

        # Format the data
        top_n_parts = []
        for key in sorted_keys:
            part = self._bom[key]
            part['NumOccurrences'] = self._counter.get(key)
            part['ReferenceDesignators'] = sorted(
                list(part['ReferenceDesignators']))
            top_n_parts.append(part)

        return top_n_parts

    def _insert_bom_line(self, manufacturer, mpn, reference_designators):
        """Insert a BOM line into the internal BOM dict.

        Args:
            manufacturer (str): Manufacturer name
            mpn (str): Manufacturer Part Number
            reference_designators (list<str>): refs to this part in the design
        """
        if self._bom is None:
            self._bom = {}

        key = manufacturer + mpn

        if key in self._bom:
            self._bom[key]['ReferenceDesignators'] |= reference_designators
        else:
            self._bom[key] = {
                'Manufacturer': manufacturer,
                'MPN': mpn,
                'ReferenceDesignators': reference_designators
            }
        self._counter.update({key: 1})


if __name__ == '__main__':
    """Entry point for the script from the command line.

    Parses args for input file path, creates a BOMReader using that file,
    and prints the top N parts.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='the input BOM file')
    args = parser.parse_args()

    bom_reader = BOMReader(args.input_file)

    printer = pprint.PrettyPrinter(indent=4)
    printer.pprint(bom_reader.get_top_n_parts())
