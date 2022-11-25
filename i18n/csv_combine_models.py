#!/usr/bin/python3

#    Copyright (C) 2021  Tor-Einar Skog,  NIBIO
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# NOT IMPLEMENTED

# Author: Tor-Einar Skog <tor-einar.skog@nibio.no>

import os
import sys
import csv
from datetime import datetime

if len(sys.argv) == 1:
    print("Usage: ./csv_to_properties.py [file_expression]")
    exit(0)

#print(sys.argv[1:])

files = sys.argv[1:]
# Make sure that we only have csv files in the list
files_ok = True
for file_name in files:
    if not file_name.endswith(".csv"):
        files_ok = False
        print("File %s is not a CSV file." % file_name)
if not files_ok:
    exit(1)

separator = ";"

# Let's do this!
for file_name in files:
    pass


print("NOT IMPLEMENTED")