#!/usr/bin/env python
leet = {
    'A': 4,
    'E': 3,
    'G': 6,
    'I': 1,
    'O': 0,
    'S': 5,
    'Z': 2,
}
in_str = input()
spritted_str = list(in_str)
result = list()
for s in spritted_str:
    if s in leet:
        s = leet[s]
    result.append(s)
for s in result:
    print("%s" % s, end='')
print()
