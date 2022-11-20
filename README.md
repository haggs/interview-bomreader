# BOM Reader
A utility for reading bills of material (BOMs).

Author: Dan Haggerty (daniel.r.haggerty@gmail.com)

Date: Jan. 11th, 2018

This module provides a BOMReader class and a command-line tool for reading a
BOM file (text). BOM files contain a value (referred to as n) in the first
line, and a list of parts in the other lines. n is the number of top-n
occurring parts to be listed. Parts can appear in the BOM file in one of three
formats.

BOMReader parses manufacturer, MPN, and the list of reference designators
from each line, and keeps a counter of the number of occurrences of
each part.

## Usage
python bomdotcom.py test_files/example.bom

python bomdotcom_test.py

## Example BOM file
2

Wintermute Systems -- CASE-19201:A2,A3

AXXX-1000:Panasonic:D1,D8,D9

Z1,Z3;40001;Keystone

Z1,Z3,Z8;40001;Keystone

