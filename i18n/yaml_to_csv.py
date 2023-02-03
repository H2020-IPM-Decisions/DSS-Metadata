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

# Extract translatable properties from YAML file and 
# * Create a new CSV file OR
# * Edit an existing CSV file. Using the one in csv_from_excel, writing the new one in csv_from_yaml
#
# Author: Tor-Einar Skog <tor-einar.skog@nibio.no>


import sys
import os
import yaml
import json
from flatten_json import flatten
import csv

# Input check
if len(sys.argv) == 1:
    print("Usage: ./yaml_to_csv.py [file_expression]")
    exit(0)

files = sys.argv[1:]

# Make sure that we only have YAML files in the list
files_ok = True
for file_name in files:
    if not file_name.endswith(".yaml"):
        files_ok = False
        print("File %s is not a YAML file." % file_name)
if not files_ok:
    exit(1)

csv_indir = "csv_from_excel" # The latest version of CSV with translations (from previous release)
csv_outdir = "csv_from_yaml"
separator = ";"

# Specific properties in the input schema
props_of_interest = ("title", "description","infoText")

# Stripping/escaping stuff that could cause trouble in file transformations
def make_csv_compatible_value(candidate):
    return candidate.replace("\"", "\\\"") if candidate is not None else ""

for file_name in files:
    print(file_name)
    # The set of translatable properties, built for each DSS (with 1->many models)
    props = {}
    with open(file_name) as f:
        dss_metadata = yaml.safe_load(f)
        ## Build the namespace / paths
        base_path = "%s.%s" % (dss_metadata["id"], dss_metadata["version"].replace(".","_"))
        props["%s.name" % base_path] = dss_metadata["name"]
        # Looping through DSS model list
        for model in dss_metadata["models"]:
            model_path = "%s.models.%s" % (base_path, model["id"])
            print("Model path: %s" % model_path)
            # Basics
            for prop_label in ["name","purpose","description"]:
                props["%s.%s" % (model_path, prop_label)] = make_csv_compatible_value(model[prop_label])
            # Warning status interpretation (implicitly ordered list)
            i=0
            for wsi in model["output"]["warning_status_interpretation"]:
                props["%s.output.warning_status_interpretation.%s.explanation" % (model_path,i)] = make_csv_compatible_value(wsi["explanation"])
                props["%s.output.warning_status_interpretation.%s.recommended_action" % (model_path,i)] = make_csv_compatible_value(wsi["recommended_action"])
                #print(wsi)
                i = i+1
            # Charts
            props["%s.output.chart_heading" % model_path] = make_csv_compatible_value(model["output"].get("chart_heading",""))
            for cg in model["output"]["chart_groups"]:
                if cg.get("id", None) is not None and cg["id"] != "":
                    props["%s.output.chart_groups.%s.title" % (model_path, cg["id"])] = make_csv_compatible_value(cg["title"])
            # Result parameters
            for rp in model["output"]["result_parameters"]:
                if rp.get("id", None) is not None and rp["id"] != "":
                    props["%s.output.result_parameters.%s.title" % (model_path, rp["id"])] = make_csv_compatible_value(rp["title"])
                    props["%s.output.result_parameters.%s.description" % (model_path, rp["id"])] = make_csv_compatible_value(rp["description"])
            
            try:
                input_schema_flattened = flatten(json.loads(model["execution"]["input_schema"]),".")
                for prop in input_schema_flattened:
                    if prop.endswith(props_of_interest):
                        props["%s.execution.input_schema.%s" % (model_path,prop)] = input_schema_flattened[prop]
            except (ValueError, json.decoder.JSONDecodeError) as e:
                pass

            props = dict(sorted(props.items()))  

    #print(props)
    #exit(0)
            
    # Writing to CSV
    # Check if file exists
    csv_input_file_path = "%s/%s.csv" % (csv_indir, dss_metadata["id"])
    csv_output_file_path = "%s/%s_TEST.csv" % (csv_outdir, dss_metadata["id"])
    if not os.path.exists(csv_input_file_path):
        # New file
        with open(csv_output_file_path, "w") as f:
            csvwriter = csv.writer(f, delimiter=";",quotechar="\"")    
            csvwriter.writerow(["KEY","default"])
            for key in props:
                csvwriter.writerow([key, props[key]])  
        print("Produced new CSV file %s" % csv_output_file_path)
    else:
        print("File exists!")
        # Read existing file
        old_content = {}
        old_header = []
        with open(csv_input_file_path, "r") as f:
            csvreader = csv.reader(f, delimiter=";",quotechar="\"")
            for row in csvreader:
                if row[0].lower() != "key":
                    old_content[row[0]] = row
                else:
                    old_header = row
        # Check that structure is intact
        # DO WE NEED TO DO THIS??
        """
        # Must be same length
        validation_ok = True
        if len(old_content) != len(props):
            print("ERROR: new content for %s has %s properties, old content has %s." % (file_name, len(old_content), len(props)))
            validation_ok = False
        # Keysets must be identical
        for p in old_content:
            if props.get(p,None) is None:
                print("ERROR: for file %s, %s exists, but is missing in the new content. Exiting." % (file_name, p))
                validation_ok = False
        for p in props:
            if old_content.get(p, None) is None:
                print("ERROR: In the new content, %s exists, but is missing in the file %s. Exiting." % (p, file_name))
                validation_ok = False
        if not validation_ok:
            print("Exiting due to errors")
            exit(1)
        """

        # Delete props in old_content that are not part of the new content
        obsolete_props = []
        for p in old_content:
            if props.get(p) is None:
                obsolete_props.append(p)
        for obsolete_prop in obsolete_props:
            old_content.pop(obsolete_prop)
        # Add props that are part of new content and not currently in old_content
        for p in props:
            if old_content.get(p) is None:
                old_content[p] = [p, props[p]]
        # Replacing contents of the default column
        for p in old_content:
            old_content[p][1] = props[p]
        with open(csv_output_file_path, "w") as f:
            csvwriter = csv.writer(f, delimiter=";",quotechar="\"")    
            csvwriter.writerow(old_header)
            all_props = list(old_content)
            all_props.sort
            for prop in all_props:
                csvwriter.writerow(old_content[prop]) 
        print("Changed CSV file %s" % csv_output_file_path)
    #print(props)

        