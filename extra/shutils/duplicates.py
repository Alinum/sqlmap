#!/usr/bin/env python


"""
Copyright (c) 2006-2012 sqlmap developers (http://www.sqlmap.org/)
See the file 'doc/COPYING' for copying permission

# Removes duplicate entries in wordlist like files

import sys

if len(sys.argv) > 0:

items = list()
f = open(sys.argv[1], 'r')

for item in f.readlines():
item = item.strip()
try:
str.encode(item)
if item in items:
if item:
print item
else:
items.append(item)

if not item:
items.append('')
except:
pass
f.close()

f = open(sys.argv[1], 'w+')
f.writelines("\n".join(items))