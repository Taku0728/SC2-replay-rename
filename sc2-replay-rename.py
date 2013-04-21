#!/usr/bin/python2

import argparse
import datetime
import hashlib
import os
import re
import sc2reader
import sys
import time

# 2012-03-29 23-07-34 PvT batrick (P) vs Fuzzzy (T) Ohana LE.SC2Replay
DEFAULT_FORMAT = "/date/ /time/ /map/ /matchup/ /teams/./version/.SC2Replay"

parser = argparse.ArgumentParser(description = "Format Starcraft II Replay File Name.")
parser.add_argument("-f", "--format", nargs = 1, default = DEFAULT_FORMAT, help = "format for the filename", dest = "format")
parser.add_argument("-l", "--ladder", action = "store_true", default = False, help = "rename ladder replays", dest = "ladder")
parser.add_argument("-m", "--melee", action = "store_true", default = False, help = "rename melee custom replays", dest = "melee")
parser.add_argument("files", nargs = "+", help = "files to rename", metavar = "file")
args = parser.parse_args()

def hashfile (path):
    sha1 = hashlib.sha1()
    f = open(path, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
        return sha1.hexdigest()

def formatteam (replay):
    matchup = []
    names = []
    teams = [[player for player in team.players] for team in replay.teams]
    for team in teams:
        team.sort(lambda a, b: cmp(a.name.lower(), b.name.lower()))
        names.append((", ").join(["%s (%s)" % (player.name, player.pick_race[0]) for player in team]))
        makeup = [player.pick_race[0] for player in team]
        matchup.append(("").join(makeup))
    matchup = ("v").join(matchup)
    return {"matchup": matchup, "teams": names}

# TODO adjust date to account for DST
options = {
  "/category/": lambda (replay): replay.category,
  "/date/": lambda (replay): replay.date.strftime("%Y-%m-%d"),
  "/length/": lambda (replay): "0", #replay.length,
  "/map/": lambda (replay): replay.map_name,
  "/matchup/": lambda (replay): formatteam(replay)["matchup"],
  "/teams/": lambda (replay): (" vs ").join(formatteam(replay)["teams"]),
  "/time/": lambda (replay): replay.date.strftime("%H-%M-%S"),
  "/type/": lambda (replay): replay.type,
  "/utcdate/": lambda (replay): replay.date.strftime("%Y-%m-%d"),
  "/utctime/": lambda (replay): replay.date.strftime("%H-%M-%S"),
  "/version/": lambda (replay): replay.release_string,
}

pattern = re.compile("/[^/]*/")
def replay_filename (replay):
    def replace (option):
        return options[option.group(0)](replay)
    return pattern.sub(replace, args.format)

for f in args.files:
    try:
        replay = sc2reader.load_replay(f)
        nf = replay_filename(replay)
        if f == nf:
            continue;
        if os.access(nf, os.F_OK):
            sys.stderr.write("cannot rename replay `%s' to `%s': destination exists" % (f, nf))
            continue;
        sys.stderr.write("`%s' -> `%s'\n" % (f, nf));
        os.rename(f, nf)
    except Exception as e:
        h = hashfile(f)+".SC2Replay"
        sys.stderr.write("could not load %s: %s; renaming to %s\n" % (f, e, h))
        os.rename(f, h)
