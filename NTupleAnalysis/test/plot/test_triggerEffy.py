#!/usr/bin/env python3
import ROOT

def get_efficiency_graph(hP, hT, bin_ls=[]):
    hP1, hT1 = hP.Clone(), hT.Clone()

#    hP1 = get_rebinned_histo(hP1, bin_ls)
#    hT1 = get_rebinned_histo(hT1, bin_ls)

    eff = ROOT.TGraphAsymmErrors(hP1, hT1, 'cl=0.683 b(1,1) mode')

    del hP1, hT1

    return eff

def main():
    ifile = ROOT.TFile.Open('L1Scouting_Run2026D.root')

    ofile = ROOT.TFile('tmp.root', 'recreate')
    ofile.cd()

    for key in ifile.GetListOfKeys():
        keyName = key.GetName()

        if not('Opt1' in keyName and keyName.endswith('PassFilterDijetEt30_J1J2_mass')):
            continue

        print(keyName)

        hT = ifile.Get(keyName.replace('PassFilterDijetEt30', ''))
        hP = ifile.Get(keyName)

        geff = get_efficiency_graph(hP, hT)
        geff.SetName(keyName)
        geff.Write()

    ofile.Close()

if __name__ == '__main__':
    main()
