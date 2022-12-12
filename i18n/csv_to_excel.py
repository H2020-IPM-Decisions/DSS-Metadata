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

# Creates a separate Excel file for each DSS CSV file, with one sheet per model
# Stores Excel files in 
# Author: Tor-Einar Skog <tor-einar.skog@nibio.no>

import sys
import csv
from pathlib import Path
import pandas as pd

# Input check
if len(sys.argv) == 1:
    print("Usage: ./csv_to_excel.py [file_expression]")
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

excel_indir = "excel_to_translation"
separator = ";"

# File by file
for file_name in files:
    #print(file_name)
    dss_id=Path(file_name).stem
    dss_table = pd.read_csv(file_name, sep=";",quotechar="\"")#, index_col=0)
    dss_main_sheet = dss_table[dss_table["KEY"].str.match(r"^(?!.*models)")]
    dss_models = {}
    with open(file_name) as csvfile:
        rowreader = csv.reader(csvfile, delimiter=separator, quotechar="\"")
        first = True
        fieldnames = []
        # Probably very un-pythonic, but I'm in a hurry!
        for row in rowreader:
            if first:
                first = False
                fieldnames = row
                continue
            key = row[0]
            if not "models" in key:
                continue
            model_name = key[key.index("models.")+len("models."):].split(".")[0]
            if dss_models.get(model_name,None) is None:
                dss_models[model_name] = []
                dss_models[model_name].append(fieldnames)
            dss_models[model_name].append(row)

    dss_models_dataframe = {}
    for model_name in dss_models:
        dss_models_dataframe[model_name] = pd.DataFrame(dss_models[model_name])
    
    # Pandas to the rescue!!! :-D
    # https://pandas.pydata.org/docs/user_guide/io.html#io-excel-writer
    excel_file_path = "%s/%s.xlsx" % (excel_indir, dss_id)
    if Path(excel_file_path).exists():
        user_input= input("%s exists. Overwrite? (y/N)" % excel_file_path)
        overwrite = True if user_input.lower() == "y" else False
        #print(("user_input=%s, overwrite=%s" % (user_input,overwrite)))
        if not overwrite:
            print("Skipping %s" % excel_file_path)
            continue
    with pd.ExcelWriter(excel_file_path) as writer:
        dss_main_sheet.to_excel(writer, sheet_name="main", index=False)
        for model_name in dss_models:
            dss_models_dataframe[model_name].to_excel(writer, 
            sheet_name=model_name,
            index=False,
            header=False
            )
    print("Produced %s" % excel_file_path)
