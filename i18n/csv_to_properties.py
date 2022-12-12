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

# Converts a csv translation file into a set of properties files
# that can form a Java ResourceBundle: https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ResourceBundle.html
# Author: Tor-Einar Skog <tor-einar.skog@nibio.no>

import os
import sys
import csv
from pathlib import Path
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
    with open(file_name) as csvfile:
        rowreader = csv.DictReader(csvfile, delimiter=separator, quotechar="\"")
        ## Checking field names
        if rowreader.fieldnames == None or not rowreader.fieldnames[0] == "KEY" or not rowreader.fieldnames[1] == "default":
            print("WARNING: Illegal or missing field headers in %s. Ignoring it." % file_name)
            continue
        #print("Field names: %s" % rowreader.fieldnames)
        base_file_name = Path(file_name).stem
        #print(base_file_name)
        # The filename equals the DSS id (by convention)
        # So the path can be deducted from it
        base_file_name = base_file_name.replace(".","/")
        path_elements = base_file_name.split("/")
        base_file_name = path_elements[len(path_elements)-1]
        path = "/".join(path_elements[0:len(path_elements)-1])
        #print (path)
        #print(base_file_name)
        props_all = {}
        for lang in rowreader.fieldnames[1:]:
            props_for_lang = {}
            props_all[lang] = props_for_lang
        for row in rowreader:
            for lang in rowreader.fieldnames[1:]:
                props_for_lang = props_all[lang]
                props_for_lang[row["KEY"]] = row[lang]
        for lang in props_all.keys():
            props_for_lang = props_all[lang]
            properties_file_name = ("%s_%s.properties" % (base_file_name, lang)) if lang != "default" else "%s.properties" % base_file_name
            if not os.path.exists(path):
                os.makedirs(path)
            with open("/".join([path,properties_file_name]),"w") as propertiesfile:
                propertiesfile.write("#\n# Auto-generated %s from %s using the csv_to_properties.py script\n#\n\n" % (datetime.now(),file_name))
                for property_key in props_for_lang.keys():
                    propertiesfile.write("%s=%s\n" % (property_key,props_for_lang[property_key].replace("\n","\\n")))


