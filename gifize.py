import os
from Plots import MakeGif

for i in range(50):
    files = sorted(filter( lambda x: 'evt{0}slice'.format(i) in x, os.listdir('old/pngs')))
    if not files: continue
    MakeGif( [ f[:-4] for f in files ], 'old/pngs/', output = 'old/evt{0}'.format(i) )
