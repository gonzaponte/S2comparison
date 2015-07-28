import os
from Plots import MakeGif
from ROOT import *

if not os.path.exists('comparison'): os.mkdir( 'comparison' )

gROOT.SetBatch()

new = TFile( 'new/new_slices.root' )
old = TFile( 'old/old_slices.root' )

ks_new = map( TKey.GetName, new.GetListOfKeys() )
ks_old = map( TKey.GetName, old.GetListOfKeys() )

nevts = 50

hdummy = new.Get( ks_new[0] ).Clone()
hdummy.Reset()

for e in range(nevts):
    print e
    new_names = filter( lambda x: x.split('_')[0] == str(e), ks_new )
    old_names = filter( lambda x: x.split('_')[0] == str(e), ks_old )
    n_new = len( new_names )
    n_old = len( old_names )
    for i in range( max( n_new, n_old ) ):
        c = TCanvas()
        c.Divide(2)
        hnew = new.Get( new_names[i] ) if i < n_new else hdummy.Clone()
        hold = old.Get( old_names[i] ) if i < n_old else hdummy.Clone()
        c.cd(1); hnew.Draw('zcol')
        c.cd(2); hold.Draw('zcol')
        c.SaveAs( 'comparison/evt{0}_{1}.png'.format(e,i) )

    if not max(n_new + n_old): continue
    MakeGif( [ 'evt{0}_{1}'.format(e,i) for i in range( max(n_new,n_old) ) ], 'comparison/', output = 'comparison/evt{0}'.format(e) )


