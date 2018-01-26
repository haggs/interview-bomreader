"""Unit tests for the BOMReader class.

Author:
    Dan Haggerty (daniel.r.haggerty@gmail.com)
Date:
    Jan. 11th, 2018

TODO:
    It's more readable if the test data isn't in different files, but
    in rather in this file.

Usage:
    python bomdotcom_test.py
"""
import bomdotcom
import unittest


class TestBomReader(unittest.TestCase):
    """Unit tests for TestBomReader.

    Reads a few BOM files, tests results of bomdotcom.BOMReader.read()
    and bomdotcom.BOMReader.get_top_n_parts()
    """
    def test_get_top_n_parts_is_correct(self):
        """get_top_n_parts() should return correct data.

        Results should be sorted by NumOccurrence and ties should go to
        the part with the higher count of ReferenceDesignators.
        """
        bom_reader = bomdotcom.BOMReader('test_files/example.bom')
        top_n_parts = bom_reader.get_top_n_parts()
        expected = [
            {
                'MPN': '40001',
                'Manufacturer': 'Keystone',
                'ReferenceDesignators': ['Z1', 'Z3', 'Z8'],
                'NumOccurrences': 2
            },
            {
                'MPN': 'AXXX-1000',
                'Manufacturer': 'Panasonic',
                'ReferenceDesignators': ['D1', 'D8', 'D9'],
                'NumOccurrences': 1
            }
        ]

        self.assertEqual(expected, top_n_parts)

    def test_get_top_n_parts_raises_with_empty_bom(self):
        """get_top_n_parts() should raise if nothing's been read yet."""
        bom_reader = bomdotcom.BOMReader()
        with self.assertRaises(bomdotcom.BOMNotInstantiatedError):
            bom_reader.get_top_n_parts()

    def test_read_called_again_clears_original_bom(self):
        """read() should clear everything between calls."""
        bom_reader = bomdotcom.BOMReader('test_files/example.bom')
        top_n_parts_before = bom_reader.get_top_n_parts()
        bom_reader.read('test_files/example2.bom')
        top_n_parts_after = bom_reader.get_top_n_parts()

        expected_part = {
            'MPN': 'AXXX-1000',
            'Manufacturer': 'Panasonic',
            'ReferenceDesignators': ['D1', 'D8', 'D9'],
            'NumOccurrences': 1
        }

        self.assertIn(expected_part, top_n_parts_before)
        self.assertNotIn(expected_part, top_n_parts_after)

    def test_read_raises_with_higher_n_than_num_parts(self):
        """read() raises BOMReadError if n is too big."""
        with self.assertRaises(bomdotcom.BOMReadError):
            bomdotcom.BOMReader('test_files/n_too_high.bom')

    def test_read_raises_with_unexpected_line_format(self):
        """Unexpected format of BOM file line should raise."""
        with self.assertRaises(bomdotcom.BOMReadError):
            bomdotcom.BOMReader('test_files/unexpected_format.bom')

    def test_parse_line_parses_format_1(self):
        """Lines that fit format 1 should be parsed."""
        bom_line = 'AXXX-1000:Panasonic:D1,D8,D9'
        expected = ('Panasonic', 'AXXX-1000', set(['D1', 'D8', 'D9']))
        result = bomdotcom.parse_line(bom_line)

        self.assertEqual(expected, result)

    def test_parse_line_parses_format_2(self):
        """Lines that fit format 2 should be parsed."""
        bom_line = 'Wintermute Systems -- CASE-19201:A2,A3'
        expected = ('Wintermute Systems', 'CASE-19201', set(['A2', 'A3']))
        result = bomdotcom.parse_line(bom_line)

        self.assertEqual(expected, result)

    def test_parse_line_parses_format_3(self):
        """Lines that fit format 3 should be parsed."""
        bom_line = 'Z1,Z3;40001;Keystone'
        expected = ('Keystone', '40001', set(['Z1', 'Z3']))
        result = bomdotcom.parse_line(bom_line)

        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
