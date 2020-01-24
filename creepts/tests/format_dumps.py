import argparse
import os
import re
import sys
import json

STEP_NUMBER = 'step_number'
FILENAME_PATTERN_REGEX="^instance_step_\d+[.]json$"
STEP_CAPTURE_PATTERN_REGEX="^instance_step_(?P<{}>\d+)[.]json$".format(STEP_NUMBER)

description = "This is a helper tool to manipulate the raw dumped states from the dispatcher"
parser = argparse.ArgumentParser(description=description)
parser.add_argument(
    '--directory', '-d',
    dest='dir',
    required=True,
    help='Directory to look for raw dispatcher dumps, you may provide an absolute path or a path relative to the directory this tool is being called from'
)
parser.add_argument(
    '--dont-beautify', '-db',
    dest='dont_beautify',
    action='store_true',
    help='Specify not to beautify the processed jsons (indent and reformat the data section of every contract level)'
)
parser.add_argument(
    '--step-as-tournament-id', '-s',
    dest='step_as_tour_id',
    action='store_true',
    help='Specify to replace the tournament id by the step number'
)
parser.add_argument(
    '--use-sufix', '-u',
    dest='sufix',
    help='Sufix to append to all output files'
)
parser.add_argument(
    '--print', '-p',
    dest='print',
    action='store_true',
    help='Print to stdout the final processed dump'
)

args = parser.parse_args()

if not os.path.isdir(args.dir):
    print("Provided path is not a valid directory path")
    sys.exit(1)

failed_files = []
pat = re.compile(FILENAME_PATTERN_REGEX)
step_pat = None
step_num_hex = None
sufix = "_pretty.json"

if args.sufix:
    sufix = args.sufix

if args.step_as_tour_id:
    step_pat = re.compile(STEP_CAPTURE_PATTERN_REGEX)

#Get an iterator for the entries of the directory
with os.scandir(args.dir) as it:

    #Go through the entries
    for entry in it:
        #Checking if entry corresponds to a file that matches the expected filename pattern
        if entry.is_file() and re.search(pat, entry.name):
            print("Will process file {}".format(entry.name))
            filename = "{}/{}".format(args.dir,entry.name)
            with open(filename) as log_file:
                state_json = None
                state = None
                try:
                    state = json.loads(log_file.read())
                except Exception as e:
                    print("Error loading file {} as a json".format(filename))
                    print(e)
                    failed_files.append(filename)
                    continue

                if not state:
                    failed_files.append(filename)
                    continue

                #Checking if should overwrite the dapp id with the step number
                if args.step_as_tour_id:
                    #Extracting step number from filename
                    match = step_pat.match(entry.name)

                    if not match:
                        print("Failed to extract step from filename {}".format(filename))
                        failed_files.append(filename)
                        continue

                    if STEP_NUMBER not in match.groupdict().keys():
                        print("Failed to extract step from filename {}".format(filename))
                        failed_files.append(filename)
                        continue

                    try:
                        step_num_hex = hex(int(match.groupdict()[STEP_NUMBER]))
                    except Exception as e:
                        print("Failed to convert step number into hex format for filename {}".format(filename))
                        failed_files.append(filename)
                        continue

                    if 'index' in state:
                        state['index']=str(step_num_hex)

                if args.dont_beautify:
                    state_json = json.dumps(state)
                else:
                    #Navigate the state tree to convert all subinstances raw json data
                    instances_to_parse = [state]
                    while instances_to_parse:
                        #Get next instance to handle
                        cur = instances_to_parse.pop(0)
                        if "sub_instances" in cur.keys():
                            if isinstance(cur["sub_instances"], list):
                                #Add children as pending
                                instances_to_parse += cur["sub_instances"]

                        #Convert raw json data if needed
                        if "json_data" in cur.keys():
                            if isinstance(cur["json_data"], str):
                                cur["json_data"] = json.loads(cur["json_data"])

                    state_json = json.dumps(state, indent=4)

                #Saving the processed json in a new file
                out_filename = filename.strip(".json") + sufix

                with open(out_filename, 'w') as out_file:
                    out_file.write(state_json)

                if args.print:
                    print('=' * 120)
                    print(state_json)
                    print('=' * 120)

                print("Processed file was saved in {}".format(out_filename))

if failed_files:
    print("\nFailed to process files: {}".format(failed_files))
