#!/usr/bin/env python3
import ROOT

#drap = [0.001, 5.999]
#dphi = [0.001, 3.140]
#drap = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
#dphi = [2.1, 3.0, 3.14]
#drap = [0.001, 0.101, 0.201, 0.301, 0.401, 0.501, 0.601, 0.701, 0.801, 0.901, 1.001, 1.099]
#dphi = [2.100, 2.501, 2.801, 3.001, 3.051, 3.140]
drap = [0.0, 0.5, 1.0, 1.5, 2.0]
dphi = [2.1, 3.0, 3.14]

eps = 0.0001

hos = []

hname = 'L1SCaloJet_Std_Mjj150_J1J2_deltaRapAbs_deltaPhiAbs'
#hname = 'L1SCaloJet_Std_Mjj150_J1J2_deltaPhiAbs'

fd = ROOT.TFile.Open('out_261112_sel0/L1ScoutingSelection_Run2026D.root')
hd = fd.Get(hname)

is_2d = hd.InheritsFrom('TH2')

sobs = []

for smass in [200, 300, 400, 500]:

    fs_name = f'out_261112_sel0/ZprimeToQQ_M{smass}_TuneCP5_13p6TeV_pythia8.root'
    fs = ROOT.TFile.Open(fs_name)
    hs = fs.Get(hname)

    ho = hs.Clone()
    ho.SetDirectory(0)
    ho.Reset()

    if is_2d:
        for xbin in range(1, ho.GetNbinsX()+1):
            for ybin in range(1, ho.GetNbinsY()+1):
                bval = hd.GetBinContent(xbin, ybin)
                sval = hs.GetBinContent(xbin, ybin)
                oval = sval*sval/bval if bval > 0 else 0
                ho.SetBinContent(xbin, ybin, oval)

        sobs_val = 0
        for drap_idx in range(1, len(drap)):
            for dphi_idx in range(1, len(dphi)):
                bval = hd.Integral(hd.GetXaxis().FindBin(+eps + drap[drap_idx-1]),
                                   hd.GetXaxis().FindBin(-eps + drap[drap_idx]),
                                   hd.GetYaxis().FindBin(+eps + dphi[dphi_idx-1]),
                                   hd.GetYaxis().FindBin(-eps + dphi[dphi_idx]))
                sval = hs.Integral(hs.GetXaxis().FindBin(+eps + drap[drap_idx-1]),
                                   hs.GetXaxis().FindBin(-eps + drap[drap_idx]),
                                   hs.GetYaxis().FindBin(+eps + dphi[dphi_idx-1]),
                                   hs.GetYaxis().FindBin(-eps + dphi[dphi_idx]))
                if sval < 1e4:
                    print(sval, drap[drap_idx-1], drap[drap_idx], dphi[dphi_idx-1], dphi[dphi_idx])

                sob = sval*sval/bval if bval > 0 else 0
                sobs_val += sob

#                print(smass, f'{drap[drap_idx-1]: >8.2f}', f'{drap[drap_idx]: >8.2f}', f'{dphi[dphi_idx-1]: >8.2f}', f'{dphi[dphi_idx]: >8.2f}', f'{bval: >19.1f}', f'{sval: >19.1f}', f'{sob: >19.1f}')

        sobs.append(sobs_val)

    else:
        for xbin in range(1, ho.GetNbinsX()+1):
            bval = hd.GetBinContent(xbin)
            sval = hs.GetBinContent(xbin)
            oval = sval*sval/bval if bval > 0 else 0
            ho.SetBinContent(xbin, oval)

    hos.append(ho)

    fs.Close()

fd.Close()

if is_2d:
    print('='*25)
    print(drap)
    print(dphi)
    print(sobs)
    print('='*25)
