#!/usr/bin/python3

#    Copyright (C) 2022  Tor-Einar Skog,  NIBIO
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


# Creates a DSS CSV file for each Excel file, combining sheets
# Stores CSV files in csv_outdir ("csv_out/")
# Author: Tor-Einar Skog <tor-einar.skog@nibio.no>


import sys
import pandas as pd
from pathlib import Path

# Input check
if len(sys.argv) == 1:
    print("Usage: ./excel_to_csv.py [file_expression]")
    exit(0)

#print(sys.argv[1:])

files = sys.argv[1:]

# Make sure that we only have Excel files in the list
files_ok = True
for file_name in files:
    if not file_name.endswith(".xlsx"):
        files_ok = False
        print("File %s is not an Excel file." % file_name)
if not files_ok:
    exit(1)

csv_outdir = "csv_from_excel"
separator = ";"

# File by file
for file_name in files:
    csv_file_path = "%s/%s.csv" % (csv_outdir, Path(file_name).stem)
    if Path(csv_file_path).exists():
        user_input= input("%s exists. Overwrite? (y/N)" % csv_file_path)
        overwrite = True if user_input.lower() == "y" else False
        #print(("user_input=%s, overwrite=%s" % (user_input,overwrite)))
        if not overwrite:
            print("Skipping %s" % csv_file_path)
            continue
    frames = []
    # Read Excel file with pandas
    # https://pandas.pydata.org/docs/user_guide/io.html#io-excel-reader
    with pd.ExcelFile(file_name) as reader:
        for s_name in reader.sheet_names:
            sheet_frame = pd.read_excel(reader, s_name)
            frames.append(sheet_frame)
        # Combine sheets
        # The concat method keeps track of mixed up columns,
        # As long as headings are provided in each Excel sheet
        all_sheets_combined = pd.concat(frames)
        # Write CSV file with same filename (except extension) as Excel file
        
        all_sheets_combined.to_csv(csv_file_path, sep=";",quotechar="\"", index=False)
        print("Produced %s" % csv_file_path)
        