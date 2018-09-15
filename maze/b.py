#!/bin/python
text = "You can! not leave. MAZE this room MAZE without?! a MAZE ment unless you MAZE; every room in the_MAZE the Maze Exit-Manual-MAZE-is-lying if..MAZE!no!maze exists. How MAZE can MAZE if our MAZE MAZE? Lying MAZE"
clear = text.replace("!","").replace(".","").replace("?","").replace("-","").replace(";","").replace("_","").replace(" ","").replace("MAZE","").lower()
print(clear)

counts = {}

for i in range(len(clear) - 1):
    chrs = clear[i:i+2]
    counts[chrs] = counts.get(chrs, 0) + 1

s = sorted([(k, counts[k]) for k in counts], key = lambda x: counts.get(x[0]))
print(s)
