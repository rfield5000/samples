# read "moves.txt" and produce a python module.
#

import sys
import re
from optparse import OptionParser

verbose_output = True

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

verbose_output = options.verbose

positions = []

in_file = open('moves.txt', 'r')

if not in_file:
    print "COULD NOT OPEN INPUT"
    sys.exit(3)

out_file = open('MoveTable.py', 'w')

print >>out_file, "class MoveTable(object):"
print >>out_file, " move_dictionary = {"

pat = re.compile("(\d+).*(\[.*\])")

mapping = {}

while (True):
    line = in_file.readline()
    if len(line) == 0:
        break
    if verbose_output:
        print line
    mat = pat.match(line)
    if (mat != None):
        grp = mat.groups()
        mapping[int(grp[0])] = grp[1]
        if verbose_output:
            print grp
            print "  %s:%s," % grp
        print >>out_file, "  %s:%s," % grp

print >>out_file, "}"

map_keys = mapping.keys()
map_keys.sort()
count = map_keys[-1]+1
out_array = [0]*count
for key in map_keys:
    items = mapping[key]
    sum = 0
    for m in eval(items):
        sum |= (2**m)
    out_array[key] = sum
condensed_file = open("condensed_table.py", "w")
print >>condensed_file, "condensed_table = ", repr(out_array)




