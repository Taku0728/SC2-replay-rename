#!/usr/bin/python2

import argparse
import datetime
import os
import re
import sc2reader
import sys
import time

# 2012-03-29 23-07-34 PvT batrick (P) vs Fuzzzy (T) Ohana LE.SC2Replay
DEFAULT_FORMAT = "/date/ /time/ /matchup/ /ateam/ vs /bteam/ /map/.SC2Replay"

parser = argparse.ArgumentParser(description = "Format Starcraft II Replay File Name.")
parser.add_argument("-f", "--format", nargs = 1, default = DEFAULT_FORMAT, help = "format for the filename", dest = "format")
#parser.add_argument("-l", "--ladder", action = "store_true", default = False, help = "rename ladder replays", dest = "ladder")
#parser.add_argument("-m", "--melee", action = "store_true", default = False, help = "rename melee custom replays", dest = "melee")
parser.add_argument("files", nargs = "+", help = "files to rename", metavar = "file")
args = parser.parse_args()

# TODO adjust date to account for DST
options = {
  "/ateam/": lambda (replay): "ateam",
  "/bteam/": lambda (replay): "bteam",
  "/category/": lambda (replay): replay.category,
  "/date/": lambda (replay): datetime.datetime.fromtimestamp(float(replay.date.strftime("%s"))).strftime("%Y-%m-%d"),
  "/length/": lambda (replay): "0", #replay.length,
  "/map/": lambda (replay): replay.map_name,
  "/matchup/": lambda (replay): replay.type,
  "/time/": lambda (replay): datetime.datetime.fromtimestamp(float(replay.date.strftime("%s"))).strftime("%H-%M-%S"),
  "/type/": lambda (replay): replay.type,
  "/utcdate/": lambda (replay): replay.date.strftime("%Y-%m-%d"),
  "/utctime/": lambda (replay): replay.date.strftime("%H-%M-%S"),
  "/version/": lambda (replay): replay.version,
}

pattern = re.compile("/[^/]*/")
def replay_filename (replay):
    def replace (option):
        return options[option.group(0)](replay)
    return pattern.sub(replace, args.format)

for f in args.files:
    replay = sc2reader.load_replay(f)
    nf = replay_filename(replay)
    if os.access(nf, os.F_OK):
        print("cannot rename replay `%s' to `%s': destination exists" % (f, nf))
        sys.exit(1);
    sys.stderr.write("`%s' -> `%s'\n" % (f, nf));
    # os.rename(f, replay_filename(replay))
