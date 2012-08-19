#!/usr/bin/python2

import argparse
import os
import sc2reader
import sys

DEFAULT_FORMAT = ""

parser = argparse.ArgumentParser(description = "Format Starcraft II Replay File Name.")
parser.add_argument("-f", "--format", nargs = 1, default = DEFAULT_FORMAT, help = "format for the filename", dest = "format")
parser.add_argument("files", nargs = "+", help = "files to rename", metavar = "file")
args = parser.parse_args()


options = {
  "/ateam/": 1,
  "/bteam/": 1,
  "/category/": lambda (replay): replay.category,
  "/date/": lambda (replay): replay.date,
  "/length/": lambda (replay): replay.length,
  "/map/": lambda (replay): replay.map,
  "/matchup/": lambda (replay): replay.type,
  "/type/": lambda (replay): replay.type,
  "/version/": lambda (replay): replay.version,
}

def replay_filename (replay):
    return "bar" # + .SC2Replay

for f in args.files:
    replay = sc2reader.load_replay(f)
    nf = replay_filename(replay)
    if os.access(nf, os.F_OK):
        print("cannot rename replay `%s' to `%s': destination exists" % (f, nf))
        sys.exit(1);
    os.rename(f, replay_filename(replay))
