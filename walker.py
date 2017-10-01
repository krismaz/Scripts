from os import walk, path, getcwd
import sys
import os
from collections import defaultdict
import hashlib

by_size = defaultdict(list)
by_hash = defaultdict(list)

from functools import partial

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

c = 0

for d, ds, fs in walk(getcwd()):
    for f in fs:
        p = path.join(d, f)
        by_size[path.getsize(p)].append(p)
        c += 1
        if c % 500 == 0:
            print(c, 'sizes!', file=sys.stderr)

c = 0

print('Need', sum(len(l) for l in by_size.values() if len(l)>1), 'hashes!', file=sys.stderr)

for s, l in by_size.items():
    if s > 0 and len(l) > 1:
        for p in l:
            by_hash[md5sum(p)].append(p)
            c += 1
            if c % 50 == 0:
                print(c, 'hashes!', file=sys.stderr)

for h, l in by_hash.items():
    if len(l) > 1:
        print(h + ':')
        for p in l:
            print('\t' + p)

print('done')