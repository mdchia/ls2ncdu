#!/usr/bin/env python3

import sys
import os

ls_lr_output = sys.argv[1]
creation_time = os.path.getmtime(ls_lr_output)

global i
ino = 0


def parse_ls_lr_line(line):
    columns = line.split()
    global ino
    # hardcoded for `mdss ls -lR` output
    # permissions = columns[0]
    # owner = columns[2]
    # group = columns[3]
    size = columns[4]
    # datetime = " ".join(columns[5], columns[6], columns[7])

    ncdu_form = dict()
    ncdu_form["name"] = columns[8]
    ncdu_form["asize"] = size
    ncdu_form["ino"] = ino
    ino += 1
    return ncdu_form
