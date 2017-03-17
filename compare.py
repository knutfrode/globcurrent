#!/usr/bin/env python

import os
import glob

folder = 'output'
images = glob.glob(folder + '/*.png')

ids = [f[-19:-4] for f in images]
ids = list(set(ids))

print ids
for id in ids:
    command = 'eog %s/*%s.png' % (folder, id)
    os.system(command)
