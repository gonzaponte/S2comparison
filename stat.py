from ROOT import *
import sys

'''
if len(sys.argv) > 1:
    ifilename = sys.argv[1]
else:
    print 'Usage: python stat.py <inputfile>'
    raise KeyboardInterrupt()
'''

def GetCharge( h ):
    q = 0
    for i in range( 1, h.GetNbinsX() + 1 ):
        for j in range( 1, h.GetNbinsY() + 1 ):
            q += h.GetBinContent( i, j )
    return q


ifilename_new = 'new/new_slices.root'
ifilename_old = 'old/old_slices.root'

new = TFile( ifilename_new )
old = TFile( ifilename_old )
ks_new = map( TKey.GetName, new.GetListOfKeys() )
ks_old = map( TKey.GetName, old.GetListOfKeys() )

nevts = 50

def evt_charge_comparison():
    q_comp = TGraphErrors()
    x = 36000
    line = TLine(0,0,x,x)

    for i in range(nevts):
        istr = str(i)
        new_names = filter( lambda x: x.split('_')[0] == istr, ks_new )
        old_names = filter( lambda x: x.split('_')[0] == istr, ks_old )
        new_hs = map( new.Get, new_names )
        old_hs = map( old.Get, old_names )
        new_q = sum( map( GetCharge, new_hs ) )
        old_q = sum( map( GetCharge, old_hs ) )
        q_comp.SetPoint( i, old_q, new_q )
        q_comp.SetPointError( i, old_q**0.5, new_q**0.5 )


    q_comp.SetTitle('Charge comparison')
    q_comp.GetXaxis().SetTitle('q old')
    q_comp.GetYaxis().SetTitle('q new')
    q_comp.SetMarkerStyle(20)
    q_comp.SetMarkerSize(1.)

    line.SetLineWidth(2)
    line.SetLineColor(kRed)

    c1 = TCanvas()
    q_comp.Draw('AP')
    line.Draw('same')

    return c1, line, q_comp

def full_charge_comparison():
    x = 200
    q_new  = TH1F('q_new' ,'new method;Q_{SiPM};Entries',x,0,x)
    q_old  = TH1F('q_old' ,'old method;Q_{SiPM};Entries',x,0,x)
    q_comp = TH2F('q_comp','SiPM charge comparison;Q_{SiPM} old;Q_{SiPM} new',x,0,x,x,0,x)
    line = TLine(0,0,x,x)

    for i in range(nevts):
        istr = str(i)
        new_names = filter( lambda x: x.split('_')[0] == istr, ks_new )
        old_names = filter( lambda x: x.split('_')[0] == istr, ks_old )
        if len(new_names) != len(old_names): continue

        for i in range(len(new_names)):
            new_h = new.Get( new_names[i] )
            old_h = old.Get( old_names[i] )
            for i in range( 1, new_h.GetNbinsX() + 1 ):
                for j in range( 1, new_h.GetNbinsY() + 1 ):
                    new_q = new_h.GetBinContent(i,j)
                    old_q = old_h.GetBinContent(i,j)
                    if new_q or old_q:
                        q_comp.Fill( old_q, new_q )
                    if new_q and old_q:
                        q_new.Fill( new_q )
                        q_old.Fill( old_q )

    line.SetLineWidth(2)
    line.SetLineColor(kRed)
    q_old.SetLineColor(kRed)

    c1 = TCanvas()
    q_comp.Draw('zcol')
    line.Draw('same')

    c2 = TCanvas()
    q_new.Draw()
    q_old.Draw('same')
    c2.BuildLegend()
    return c1, line, q_comp, c2, q_new, q_old

def check_missing():
    q_miss = TH1F('missing','Charge of missing slices;Q;Entries',50,0,50)
    for key in ks_new:
        if not key in ks_old:
            q_miss.Fill( GetCharge( new.Get(key) ) )
    for key in ks_old:
        if not key in ks_new:
            q_miss.Fill( GetCharge( old.Get(key) ) )

    c = TCanvas()
    q_miss.Draw()
    return c, q_miss

def nslices():
    nsl = 90
    hnslices = TH2F('nslices','# slices;old;new',nsl,0,nsl,nsl,0,nsl)
    line = TLine(0,0,nsl,nsl)
    for i in range(nevts):
        istr = str(i)
        new_names = filter( lambda x: x.split('_')[0] == istr, ks_new )
        old_names = filter( lambda x: x.split('_')[0] == istr, ks_old )
        hnslices.Fill( len(old_names), len(new_names) )

    line.SetLineWidth(2)
    line.SetLineColor(kRed)

    c = TCanvas()
    hnslices.Draw('zcol')
    line.Draw('same')
    return c, hnslices,line

def nsignal():
    hnsigs = TH2F('nsignals','# signals;old;new',5,0,5,5,0,5)
    hq = TH1F('mincharge',';q;Entries',50,0,50)
    for i in range(nevts):
        istr = str(i)
        new_names = filter( lambda x: x.split('_')[0] == istr, ks_new )
        old_names = filter( lambda x: x.split('_')[0] == istr, ks_old )
        new_sigs  = len( set( x.split('_')[1] for x in new_names ) )
        old_sigs  = len( set( x.split('_')[1] for x in old_names ) )
        hnsigs.Fill( old_sigs, new_sigs )
        if old_sigs == new_sigs: continue
        names = new_names if new_sigs > old_sigs else old_names
        sigs  = max( old_sigs, new_sigs )
        file  = new if new_sigs > old_sigs else old
        sigs = [ filter( lambda x: x.split('_')[1] == str(i), names ) for i in range(sigs) ]
        charges = [ sum( GetCharge(file.Get(n)) for n in s ) for s in sigs ]
        minq = min(charges)
        hq.Fill(minq)

    c = TCanvas()
    c.Divide(2)
    c.cd(1)
    hnsigs.Draw('zcol')
    c.cd(2)
    hq.Draw()
    c.Modified()
    c.Update()
    return c, hnsigs, hq

def outsignal():

    hs_new = [ TH1F(str(i) + 'new','',20,0,20) for i in range(3)]
    hs_old = [ TH1F(str(i) + 'old','',20,0,20) for i in range(3)]

    for e in range(nevts):
        istr = str(e)
        new_slices = filter( lambda x: x.split('_')[0] == istr, ks_new )
        old_slices = filter( lambda x: x.split('_')[0] == istr, ks_old )
        for sl in new_slices:
            h = new.Get( sl )
            x0, y0 = h.GetMean(1), h.GetMean(2)
            for i in range( 1, h.GetNbinsX() + 1 ):
                for j in range( 1, h.GetNbinsY() + 1 ):
                    x = h.GetXaxis().GetBinCenter(i)
                    y = h.GetYaxis().GetBinCenter(j)
                    r2 = (x-x0)**2 + (y-y0)**2
                    if 400. <= r2 < 2500.: # 2cm
                        rbin = int( ( r2**0.5 - 20. ) // 10 )
                        q  = h.GetBinContent(i,j)
                        hs_new[rbin].Fill( q )

        for sl in old_slices:
            h = old.Get( sl )
            x0, y0 = h.GetMean(1), h.GetMean(2)
            for i in range( 1, h.GetNbinsX() + 1 ):
                for j in range( 1, h.GetNbinsY() + 1 ):
                    x = h.GetXaxis().GetBinCenter(i)
                    y = h.GetYaxis().GetBinCenter(j)
                    r2 = (x-x0)**2 + (y-y0)**2
                    if 400. <= r2 < 2500.: # 2cm
                        rbin = int( ( r2**0.5 - 20. ) // 10 )
                        q  = h.GetBinContent(i,j)
                        hs_old[rbin].Fill( q )

    c = TCanvas()
    c.Divide(3,2)
    for i in range(3):
        c.cd(i+1)
        hs_new[i].Draw()
    for i in range(3):
        c.cd(i+4)
        hs_old[i].Draw()

    c.Modified()
    c.Update()
    return c, hs_old, hs_new



#a = evt_charge_comparison()
#b = full_charge_comparison()
#c = check_missing()
#d = nslices()
#e = nsignal()
f = outsignal()
raw_input()
