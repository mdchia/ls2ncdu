#!/usr/bin/env python3

import sys
import os
import argparse
import time

# constants
majorver = "1"  # must be 1 according to spec (currently)
minorver = "0"  # indicates ncdu ver. support, 0 for ncdu >1.9, and 1 for extended mode ncdu >1.13
program = "ls2ncdu"
progver = "1.0"


# originally meant to be be the global string for storing the whole json file
# ditched for printing directly
# ncdu_json = ""


def json_add(line, level=0):
    level_char = " "
    print((level_char * level) + line)


def json_val_add(keystr, valuestr, level=0, last=False):
    level_char = " "
    if type(valuestr) is str:
        print((level_char * level) + '"' + str(keystr) + '" : "' + valuestr + '"' + ("" if last else ","))
    else:
        print((level_char * level) + '"' + str(keystr) + '" : ' + str(valuestr) + ("" if last else ","))

# doesn't actually parse ls -lR data for directory info, so assumptions on dir
# are stored in this function


def json_add_dir_entry(dirstr, level=0):
    json_add("{", level)
    json_val_add("name", dirstr, level + 1)
    json_val_add("asize", 4096, level + 1, True)
    json_add("}", level)


def main():
    ap = argparse.ArgumentParser(prog="ls2ncdu")
    ap.add_argument("input", type=argparse.FileType("r"), default=sys.stdin, nargs='?',
                    help="Output of ls -lR or similar")

    args = ap.parse_args()
    # use modification time of the ls -lR dump text file as the timestamp for
    # ncdu json (needs to be a UNIX timestamp)
    try:
        modtime = int(os.path.getmtime(args.input.name))
    except:
        modtime = int(time.time())
    base_level = 1  # starts where start() leaves off
    curr_level = base_level
    curr_node_dir = ""
    line_is_dir = True
    root_dir = None
    is_first_file = True
    is_first_dir = True
    # init file
    json_add("[")
    json_add(majorver + ",", 1)
    json_add(minorver + ",", 1)
    json_add("{", 1)
    json_val_add("progname", program, 2)
    json_val_add("progver", progver, 2)
    json_val_add("timestamp", modtime, 2, True)
    json_add("}", 1)
    # loop through data
    for line in args.input:
        if line.startswith("total"):
            continue
        if line == "\n" or line == "":
            line_is_dir = True
            is_first_file = True
            continue
        if line_is_dir:  # new dir
            if root_dir is None:
                json_add(",", curr_level)
                json_add("[", curr_level)
                root_dir = line.replace(":", "")
                root_dir = root_dir.strip()
                if root_dir.endswith("/"):
                    root_dir = root_dir.replace("/", "")  # strip for json purposes
                json_add_dir_entry(root_dir, curr_level + 1)
                if not root_dir.endswith("/"):
                    root_dir += "/"  # always end with trailing slash
                curr_level += 1
            else:
                curr_path = (line.replace(":", "")).strip()
                curr_path = curr_path.replace(root_dir, "")
                curr_dir_bits = curr_path.split("/")
                curr_depth = curr_level - base_level - 1
                # print("Depth: "+str(curr_depth)+" curr_dir_bits:"+str(len(curr_dir_bits)))  # debug
                if len(curr_dir_bits) > curr_depth:
                    json_add(",", curr_level)
                    curr_level += 1
                    json_add("[", curr_level)
                elif len(curr_dir_bits) == curr_depth:
                    json_add("],[", curr_level)
                elif len(curr_dir_bits) < curr_depth:
                    while curr_depth != len(curr_dir_bits):
                        # print("Depth: "+str(curr_depth)+" curr_dir_bits:"+str(len(curr_dir_bits)))  # debug
                        json_add("]", curr_level)
                        curr_level -= 1
                        curr_depth = curr_level - base_level - 1  # recalculate tree depth
                    json_add("],[", curr_level)
                json_add_dir_entry(curr_dir_bits[-1], curr_level + 1)
            line_is_dir = False
        else:
            columns = line.split()
            # hardcoded for `mdss ls -lR` output
            permissions = columns[0]
            if not permissions.startswith("-"):  # exclude directories/links/etc.
                continue
            # owner = columns[2]
            # group = columns[3]
            size = columns[4]
            # datetime = " ".join(columns[5], columns[6], columns[7])
            name = columns[8]
            json_add(",", curr_level)
            json_add("{", curr_level)
            json_val_add("name", columns[8], curr_level + 1)
            json_val_add("dsize", int(size), curr_level + 1)
            json_val_add("asize", int(size), curr_level + 1, True)
            json_add("}", curr_level)
    while (curr_level > base_level):
        # add final closing brackets
        json_add("]", curr_level)
        curr_level -= 1
    json_add("]")

if __name__ == "__main__":
    main()
