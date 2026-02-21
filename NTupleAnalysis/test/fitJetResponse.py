#!/usr/bin/env python3
import argparse
import os
import fnmatch
import math
import ROOT
import re

from common.utils import *
from common.th1 import *
from common.efficiency import *
from common.plot import *
from common.plot_style import *

def updateDictionary(dictionary, TDirectory, prefix='', matches=[], skip=[], verbose=False):
    key_prefix = prefix+'/' if (len(prefix) > 0) else ''
    for j_key in TDirectory.GetListOfKeys():
        j_key_name = j_key.GetName()
        j_obj = TDirectory.Get(j_key_name)
        if j_obj.InheritsFrom('TDirectory'):
           updateDictionary(dictionary, j_obj, prefix=key_prefix+j_key_name, matches=matches, skip=skip, verbose=verbose)

        elif j_obj.InheritsFrom('TH1') or j_obj.InheritsFrom('TGraph'):
           out_key = key_prefix+j_key_name

           if skip:
              skip_key = False
              for _keyw in skip:
                  if fnmatch.fnmatch(out_key, _keyw):
                     skip_key = True
                     break
              if skip_key:
                 continue

           if matches:
              skip_key = True
              for _keyw in matches:
                  if fnmatch.fnmatch(out_key, _keyw):
                     skip_key = False
                     break
              if skip_key:
                 continue

           if out_key in dictionary:
              KILL(log_prx+'input error -> found duplicate of template ["'+out_key+'"] in input file: '+TDirectory.GetName())

           dictionary[out_key] = j_obj.Clone()
           if hasattr(dictionary[out_key], 'SetDirectory'):
              dictionary[out_key].SetDirectory(0)

           if verbose:
              print(colored_text('[input]', ['1','92']), out_key)

    return dictionary

def getTH1sFromTFile(path, matches, skip, verbose=False):
    input_histos_dict = {}

    i_inptfile = ROOT.TFile.Open(path)
    if (not i_inptfile) or i_inptfile.IsZombie() or i_inptfile.TestBit(ROOT.TFile.kRecovered):
       return input_histos_dict

    updateDictionary(input_histos_dict, i_inptfile, prefix='', matches=matches, skip=skip, verbose=verbose)

    i_inptfile.Close()

    return input_histos_dict

class Histogram:
    def __init__(self):
        self.th1 = None
        self.draw = ''
        self.Legend = ''
        self.LegendDraw = ''

def fitAndPlot(histograms, outputs, title, labels, legXY=[], legNColumns=1, addLogX=False, doFit=False, ratio=False, ratioPadFrac=0.3, xMin=None, xMax=None, yMin=None, yMax=None, xMinFit=None, xMaxFit=None, yMinRatio=None, yMaxRatio=None, logX=False, logY=False, autoRangeX=False, xLabelSize=None, xBinLabels=None):

    xyMinMax = []
    if histograms[0].th1.InheritsFrom('TGraph'):
       xyMinMax = get_xyminmax_from_graph(histograms[0].th1)

    nvalid_histograms = len(histograms)

    canvas = ROOT.TCanvas('tmp', 'tmp', 900, 900)

    Top = 0.15
    Rig = 0.04
    Bot = 0.15
    Lef = 0.15

    canvas.SetTopMargin(Top)
    canvas.SetBottomMargin(Bot)
    canvas.SetLeftMargin(Lef)
    canvas.SetRightMargin(Rig)

    canvas.SetGrid(1,1)
    canvas.SetTickx()
    canvas.SetTicky()

    textPads = [
        get_text(Lef+(1-Lef-Rig)*0.00, (1-Top)+Top*0.75, 11, .03, labels[0]),
        get_text(Lef+(1-Lef-Rig)*0.00, (1-Top)+Top*0.45, 11, .03, labels[1]),
        get_text(Lef+(1-Lef-Rig)*0.00, (1-Top)+Top*0.15, 11, .03, labels[2]),
    ]

    leg = None
    if len(legXY) == 4:
       leg = ROOT.TLegend(legXY[0], legXY[1], legXY[2], legXY[3])
       leg.SetBorderSize(2)
       leg.SetTextFont(42)
       leg.SetFillColor(0)
       leg.SetNColumns(legNColumns)
       for _tmp in histograms:
           if _tmp.th1 is not None:
              if (_tmp.th1.InheritsFrom('TH1') and _tmp.th1.GetEntries()) or (_tmp.th1.InheritsFrom('TGraph') and _tmp.th1.GetN()):
                 leg.AddEntry(_tmp.th1, _tmp.Legend, _tmp.LegendDraw)

    if autoRangeX:
       xMinCalc, xMaxCalc = None, None
       for _tmp in histograms:
           if (_tmp.th1 is not None):
              if hasattr(_tmp.th1, 'GetNbinsX'):
                 tmpXMin, tmpXMax = _tmp.th1.GetBinLowEdge(1), _tmp.th1.GetBinLowEdge(1+_tmp.th1.GetNbinsX())
                 if _tmp.th1.Integral() > 0.:
                    for i_bin in range(1, _tmp.th1.GetNbinsX()+1):
                        if (_tmp.th1.GetBinContent(i_bin) != 0.) or (_tmp.th1.GetBinError(i_bin) != 0.): break
                        tmpXMin = _tmp.th1.GetBinLowEdge(i_bin)
                    for i_bin in reversed(range(1, _tmp.th1.GetNbinsX()+1)):
                        if (_tmp.th1.GetBinContent(i_bin) != 0.) or (_tmp.th1.GetBinError(i_bin) != 0.): break
                        tmpXMax = _tmp.th1.GetBinLowEdge(i_bin)
                 xMinCalc = min(xMinCalc, tmpXMin) if xMinCalc is not None else tmpXMin
                 xMaxCalc = max(xMaxCalc, tmpXMax) if xMaxCalc is not None else tmpXMax
              else:
                 _tmp_xyMinMax = get_xyminmax_from_graph(_tmp.th1)
                 xMinCalc = min(xMinCalc, _tmp_xyMinMax[0]) if xMinCalc is not None else _tmp_xyMinMax[0]
                 xMaxCalc = max(xMaxCalc, _tmp_xyMinMax[2]) if xMaxCalc is not None else _tmp_xyMinMax[2]
    else:
       xMinCalc = xyMinMax[0] if xyMinMax else histograms[0].th1.GetBinLowEdge(1)
       xMaxCalc = xyMinMax[2] if xyMinMax else histograms[0].th1.GetBinLowEdge(1+histograms[0].th1.GetNbinsX())

    XMIN = xMinCalc if xMin is None else (max(xMin, xMinCalc) if autoRangeX else xMin)
    XMAX = xMaxCalc if xMax is None else (min(xMax, xMaxCalc) if autoRangeX else xMax)

    HMIN, HMAX = 1e8, -1e8
    for _tmp in histograms:
        if (_tmp.th1 is not None):
           if hasattr(_tmp.th1, 'GetNbinsX'):
              for i_bin in range(1, _tmp.th1.GetNbinsX()+1):
                  HMAX = max(HMAX, (_tmp.th1.GetBinContent(i_bin) + _tmp.th1.GetBinError(i_bin)))
           else:
              _tmp_xyMinMax = get_xyminmax_from_graph(_tmp.th1)
              HMIN = min(HMIN, _tmp_xyMinMax[1]) if _tmp_xyMinMax[1] is not None else 0
              HMAX = max(HMAX, _tmp_xyMinMax[3]) if _tmp_xyMinMax[3] is not None else 1

    YMIN, YMAX = yMin, yMax
    if YMIN is None: YMIN = .0003 if logY else .0001
    if YMAX is None: YMAX = .0003*((HMAX/.0003)**(1./.80)) if logY else .0001+((HMAX-.0001) *(1./.80))

    tf1 = None
    if doFit:
        if len(histograms) != 1:
            KILL(f'plot -- (doFit=True) invalid number of input histograms ({len(histograms)})')

        h0 = histograms[0].th1.Clone()

        tfitres = None
        minChi2OverNdof = -1

        fit_funcs = []
#        fit_funcs += [(idx, f'pol{idx}') for idx in range(3, 12)]:
        fit_funcs += [(4, '[0]+[1]*(x/1000)+[2]*(x/1000)^2+[3]*log(x)')]

        XMIN_FIT = xMinFit if xMinFit else XMIN
        XMAX_FIT = xMaxFit if xMaxFit else XMAX

        for fitf_i in fit_funcs:
            fitf = ROOT.TF1('fitf', fitf_i[1], fitf_i[0], XMIN_FIT, XMAX_FIT)
            fitfres = h0.Fit(fitf, 'Sq')
            chi2OverNdof = fitfres.Chi2() / fitfres.Ndf()
            if fitfres.Status() == 0 and (minChi2OverNdof < 0 or chi2OverNdof < minChi2OverNdof):
                minChi2OverNdof = chi2OverNdof
                tfitres = fitfres
                tf1 = fitf

        if tf1 and tfitres:
            tf1.SetLineColor(h0.GetLineColor())
            tf1.SetLineWidth(2)
            tf1.SetLineStyle(1)

            chi2OverNdof = tfitres.Chi2() / tfitres.Ndf()
            fit_func_str = fitf.GetFormula().GetTitle()
            fit_func_str = fit_func_str.replace('+', ' + ')
            fit_func_str = fit_func_str.replace('*', ' ')
            fit_func_str = fit_func_str.replace('[0]', 'A')
            fit_func_str = fit_func_str.replace('[1]', 'B')
            fit_func_str = fit_func_str.replace('[2]', 'C')
            fit_func_str = fit_func_str.replace('[3]', 'D')
            fit_func_str = fit_func_str.replace('^2', '^{2}')
            fit_func_str = fit_func_str.replace('1000', '10^{3}')
            fitLabel = f'Fit [{XMIN_FIT}-{XMAX_FIT}]: {fit_func_str}'
            fitLabel += ' (#chi^{2}/ndf = ' + f'{chi2OverNdof:.1f})'
        else:
            WARNING(f'plot -- fit failed: {h0.GetName()}')
            fitLabel = 'FIT FAILED'

        textPads += [get_pavetext(
            Lef+(1-Lef-Rig)*0.03, Bot+(1-Bot-Top)*0.90,
            Lef+(1-Lef-Rig)*0.97, Bot+(1-Bot-Top)*0.99,
            .03, fitLabel
        )]
        textPads[-1].SetBorderSize(1)
        textPads[-1].SetFillColor(0)

    canvas.cd()

    if not ratio:

       h0 = canvas.DrawFrame(XMIN, YMIN, XMAX, YMAX)

       canvas.SetTickx()
       canvas.SetTicky()

       canvas.SetLogx(logX)
       canvas.SetLogy(logY)

       if tf1:
           tf1_tmp = tf1.Clone()
           tf1_tmp.SetLineStyle(2)
           tf1_tmp.SetRange(XMIN, XMAX)
           tf1_tmp.Draw('l,same')
           tf1.SetRange(XMIN_FIT, XMAX_FIT)
           tf1.Draw('l,same')

       for _tmp in histograms:
           if _tmp.th1 is not None:
              _tmp.th1.Draw(_tmp.draw)

       h0.Draw('axis,same')
       h0.SetTitle(title)

       if xLabelSize:
          h0.GetXaxis().SetLabelSize(xLabelSize)

       if xBinLabels:
          xBinLabels = xBinLabels[int(round(XMIN)):int(round(XMAX))]
          h0.GetXaxis().Set(len(xBinLabels), XMIN, XMAX)
          for tmpIdx, tmpLab in enumerate(xBinLabels):
              h0.GetXaxis().SetBinLabel(tmpIdx+1, tmpLab)

       if leg:
          leg.Draw('same')

       for _tmp in textPads:
           if hasattr(_tmp, 'Draw'):
              _tmp.Draw('same')

    else:
       pad1H = max(0.01, 1.-ratioPadFrac)

       pad1 = ROOT.TPad('pad1', 'pad1', 0, 1-pad1H, 1, 1)

       pad1.SetTopMargin(Top / pad1H)
       pad1.SetBottomMargin(0.02)
       pad1.SetLeftMargin(Lef)
       pad1.SetRightMargin(Rig)

       pad1.SetGrid(1,1)
       pad1.SetTickx()
       pad1.SetTicky()
       pad1.SetLogx(logX)
       pad1.SetLogy(logY)
       pad1.Draw()

       ROOT.SetOwnership(pad1, False)

       pad1.cd()

       h0 = pad1.DrawFrame(XMIN, YMIN, XMAX, YMAX)

       if tf1:
           tf1_tmp = tf1.Clone()
           tf1_tmp.SetLineStyle(2)
           tf1_tmp.SetRange(XMIN, XMAX)
           tf1_tmp.Draw('l,same')
           tf1.SetRange(XMIN_FIT, XMAX_FIT)
           tf1.Draw('l,same')

       h11 = None
       for _tmp in histograms:
           if _tmp.th1 is not None:
              if h11 is None: h11 = _tmp.th1
              _tmp.th1.Draw(_tmp.draw)

       if not h11: return 1

       h0.Draw('axis,same')
       h0.GetXaxis().SetTitle('')
       h0.GetYaxis().SetTitle(title.split(';')[2])
       h0.GetXaxis().SetRangeUser(XMIN, XMAX)

       h0.GetYaxis().SetTitleSize(h0.GetYaxis().GetTitleSize()/pad1H)
       h0.GetYaxis().SetTitleOffset(h0.GetYaxis().GetTitleOffset()*pad1H)
       h0.GetXaxis().SetLabelSize(0)
       h0.GetYaxis().SetLabelSize(h0.GetYaxis().GetLabelSize()/pad1H)
       h0.GetXaxis().SetTickLength(h0.GetXaxis().GetTickLength()/pad1H)

       if YMIN is None: YMIN = .0003 if logY else .0001
       if YMAX is None: YMAX = .0003*((HMAX/.0003)**(1./.80)) if logY else .0001+((HMAX-.0001)*(1./.80))

       h0.GetYaxis().SetRangeUser(YMIN, YMAX)

       if leg:
          leg.Draw('same')
          pad1.Update()
          leg.SetY1NDC(1.-(1.-leg.GetY1NDC())/pad1H)
          leg.SetY2NDC(1.-(1.-leg.GetY2NDC())/pad1H)

       textPads2 = []
       for _tmp in textPads:
           if hasattr(_tmp, 'Clone'):
              _tmp2 = _tmp.Clone()
              textPads2 += [_tmp2]

       for _tmp in textPads2:
           _tmp.Draw('same')
           pad1.Update()
           _tmp.SetTextSize(_tmp.GetTextSize()/pad1H)
           try:
               _tmp.SetY(1.-(1.-_tmp.GetY())/pad1H)
           except:
               _tmp.SetY1NDC(1.-(1.-_tmp.GetY1NDC())/pad1H)
               _tmp.SetY2NDC(1.-(1.-_tmp.GetY2NDC())/pad1H)

       pad1.Update()

       canvas.cd()

       pad2 = ROOT.TPad('pad2', 'pad2', 0, 0, 1, 1-pad1H)
       pad2.SetTopMargin(0)
       pad2.SetBottomMargin(Bot / (1-pad1H))
       pad2.SetLeftMargin(Lef)
       pad2.SetRightMargin(Rig)
       pad2.SetGrid(1,1)
       pad2.SetLogx(logX)
       pad2.SetTickx()
       pad2.SetTicky()
       pad2.Draw()

       denom = h11.Clone()
       if hasattr(denom, 'GetNbinsX'):
          for _tmp in range(0, denom.GetNbinsX()+2):
              denom.SetBinError(_tmp, 0.)
              if tf1:
                  denom.SetBinContent(_tmp, tf1.Eval(denom.GetBinCenter(_tmp)))
       else:
          for _tmp in range(denom.GetN()):
              denom.SetPointEYhigh(_tmp, 0.)
              denom.SetPointEYlow(_tmp, 0.)
              if tf1:
                  denom.SetPointY(_tmp, tf1.Eval(denom.GetPointX(_tmp)))

       plot_ratios = []

       for _tmp in histograms:
           histo = Histogram()
           if _tmp.th1 is not None:
              histo.th1 = _tmp.th1.Clone()
              if histo.th1.InheritsFrom('TH1'):
                 histo.th1.Divide(denom)
              else:
                 histo.th1 = get_ratio_graph(histo.th1, denom)

           histo.draw = _tmp.draw
           if _tmp.th1.InheritsFrom('TH1') and ('same' not in histo.draw):
              histo.draw += ',same'

           histo.Legend = _tmp.Legend
           histo.LegendDraw = _tmp.LegendDraw

           if hasattr(histo.th1, 'SetStats'):
              histo.th1.SetStats(0)

           plot_ratios += [histo]

       ROOT.SetOwnership(pad2, False)

       pad2.cd()

       h21 = pad2.DrawFrame(XMIN, 0., XMAX, 2.)

       h21.SetFillStyle(3017)
       h21.SetFillColor(16)

       h21.GetXaxis().SetTitle(title.split(';')[1])
       h21.GetYaxis().SetTitle('Data / Fit')
       h21.GetYaxis().CenterTitle()
       h21.GetXaxis().SetTitleSize(h21.GetXaxis().GetTitleSize()/(1-pad1H))
       h21.GetYaxis().SetTitleSize(h21.GetYaxis().GetTitleSize()/(1-pad1H) * 0.90)
       h21.GetXaxis().SetTitleOffset(h21.GetXaxis().GetTitleOffset())
       h21.GetYaxis().SetTitleOffset(h21.GetYaxis().GetTitleOffset()*(1-pad1H))
       h21.GetXaxis().SetLabelSize(h21.GetYaxis().GetLabelSize()/(1-pad1H))
       h21.GetYaxis().SetLabelSize(h21.GetYaxis().GetLabelSize()/(1-pad1H))
       h21.GetXaxis().SetTickLength(h21.GetXaxis().GetTickLength()/(1-pad1H))
       h21.GetXaxis().SetLabelOffset(h21.GetXaxis().GetLabelOffset()/(1-pad1H))
       h21.GetYaxis().SetNdivisions(404)

       if xLabelSize:
          h21.GetXaxis().SetLabelSize(xLabelSize)

       if xBinLabels:
          xBinLabels = xBinLabels[int(round(XMIN)):int(round(XMAX))]
          h21.GetXaxis().Set(len(xBinLabels), XMIN, XMAX)
          for tmpIdx, tmpLab in enumerate(xBinLabels):
              h21.GetXaxis().SetBinLabel(tmpIdx+1, tmpLab)

       h21.GetXaxis().SetRangeUser(XMIN, XMAX)

       h2max, h2min = None, None
       for _tmp in plot_ratios:
           if _tmp.th1 is None: continue
           if hasattr(_tmp.th1, 'GetNbinsX'):
              for _tmpb in range(1, _tmp.th1.GetNbinsX()+1):
                  if (abs(_tmp.th1.GetBinContent(_tmpb)) > 1e-7) and (abs(_tmp.th1.GetBinError(_tmpb)) > 1e-7):
                     h2max = max(h2max, _tmp.th1.GetBinContent(_tmpb)+_tmp.th1.GetBinError(_tmpb)) if (h2max is not None) else _tmp.th1.GetBinContent(_tmpb)+_tmp.th1.GetBinError(_tmpb)
                     h2min = min(h2min, _tmp.th1.GetBinContent(_tmpb)-_tmp.th1.GetBinError(_tmpb)) if (h2min is not None) else _tmp.th1.GetBinContent(_tmpb)-_tmp.th1.GetBinError(_tmpb)
           else:
              _tmp_xyMinMax = get_xyminmax_from_graph(_tmp.th1)
              h2min = min(h2min, _tmp_xyMinMax[1]) if ((h2min is not None) and (_tmp_xyMinMax[1] is not None)) else 0
              h2max = max(h2max, _tmp_xyMinMax[3]) if ((h2max is not None) and (_tmp_xyMinMax[3] is not None)) else 1

       if (h2max is not None) and (h2min is not None):
          h2min = min(int(h2min*105.)/100., int(h2min*95.)/100.)
          h2max = max(int(h2max*105.)/100., int(h2max*95.)/100.)

          h2min = max(h2min, -5)
          h2max = min(h2max, 5)

       YMIN_RATIO = yMinRatio if yMinRatio else h2min
       YMAX_RATIO = yMaxRatio if yMaxRatio else h2max

       if YMIN_RATIO and YMAX_RATIO:
          h21.GetYaxis().SetRangeUser(YMIN_RATIO, YMAX_RATIO)

       if tf1:
           tfOne_tmp = ROOT.TF1('tfOne_tmp', 'pol0', XMIN, XMAX)
           tfOne_tmp.SetParameter(0, 1)
           tfOne_tmp.SetRange(XMIN, XMAX)
           tfOne_tmp.SetLineWidth(tf1.GetLineWidth())
           tfOne_tmp.SetLineColor(tf1.GetLineColor())
           tfOne_tmp.SetLineStyle(2)
           tfOne_tmp.Draw('l,same')
           tfOne_tmp2 = tfOne_tmp.Clone()
           tfOne_tmp2.SetRange(XMIN_FIT, XMAX_FIT)
           tfOne_tmp2.SetLineStyle(tf1.GetLineStyle())
           tfOne_tmp2.Draw('l,same')

       for _tmp in plot_ratios:
           if _tmp.th1 is not None:
              _tmp.th1.Draw(_tmp.draw)
       h21.Draw('axis,same')

    canvas.cd()
    canvas.Update()

    for output_file in outputs:
        output_dirname = os.path.dirname(output_file)
        if not os.path.isdir(output_dirname):
           EXE('mkdir -p '+output_dirname)

        canvas.SetName(os.path.splitext(output_file)[0])
        canvas.SaveAs(output_file)

        print(colored_text('[output]', ['1', '92']), os.path.relpath(output_file))

    if addLogX:
        if ratio:
            pad1.SetLogx(True)
            pad2.SetLogx(True)
        else:
            canvas.SetLogx(True)

        for output_file in outputs:
            output_file_logX = '_logX.'.join(output_file.rsplit('.', 1))
            canvas.SaveAs(output_file_logX)
            print(colored_text('[output]', ['1', '92']), os.path.relpath(output_file_logX))

    canvas.Close()

    if ratio:
       del plot_ratios
       del denom

    return tf1

def getPlotLabels(key, keyword):

    _jetLabel = ''
    if key.startswith('GenJet_'):
        _jetLabel = 'GEN Jets'
    elif key.startswith('GenJetNoMu_'):
        _jetLabel = 'GEN Jets(NoMu)'
    elif key.startswith('L1EmulJet_'):
        _jetLabel = 'L1T Jets'
    elif key.startswith('L1EmulJet1_'):
        _jetLabel = 'L1T Jets (E_{T} < 1023.5 GeV)'
    elif key.startswith('L1EmulAK4CTJet0_'):
        _jetLabel = 'Uncorrected AK4 L1CaloTowerJets'
    elif key.startswith('L1EmulAK4CTJet0CorrA_'):
        _jetLabel = 'AK4 L1CaloTowerJets (JEC=A)'
    elif key.startswith('L1EmulAK4CTJet0Corr_'):
        _jetLabel = 'AK4 L1CaloTowerJets (Corr)'
    elif key.startswith('L1EmulAK4CTJet1_'):
        _jetLabel = 'Uncorrected AK4 L1CaloTowerJets (no E-saturated towers)'

    _selLabel = ''
    sel_match = re.match('.*_eta(\+|-)(\w+)to(\+|-)(\w+)nCTie4(\d+)to(\d+?|Inf)_.*', key)
    if sel_match:
        _selLabel += f'{sel_match.group(1)}'
        _selLabel += f'{sel_match.group(2).replace("p", ".")}'
        _selLabel += ' <= |#eta_{jet}| < '
        _selLabel += f'{sel_match.group(3)}'
        _selLabel += f'{sel_match.group(4).replace("p", ".")}'
        _selLabel += ', '
        if sel_match.group(6) == 'Inf':
            _selLabel += 'N_{CTie4} >= '
            _selLabel += f'{int(sel_match.group(5))}'
        else:
            _selLabel += f'{int(sel_match.group(5))}'
            _selLabel += ' <= N_{CTie4} < '
            _selLabel += f'{int(sel_match.group(6))}'

    ## titles of axes
    _titleX, _titleY = key, ''
    if key.endswith('_E'): _titleX = 'Jet energy [GeV]'
    elif key.endswith('_pt'): _titleX = 'Jet p_{T} [GeV]'
    elif key.endswith('_eta'): _titleX = 'Jet #eta'
    elif key.endswith('_phi'): _titleX = 'Jet #phi'

    if ('_GEN_' in key) or ('GenJet' in key):
       _titleX = 'GEN '+_titleX

    if '_E_overGEN_Mean_' in key: _titleY = '<E / E^{GEN}>'
    elif '_E_overGEN_RMSOverMean_' in key: _titleY = '#sigma(E / E^{GEN}) / <E / E^{GEN}>'
    elif '_E_overGEN_Median_' in key: _titleY = 'Median(E / E^{GEN})'
    elif '_E_overGEN_RMSOverMedian_' in key: _titleY = '#sigma(E / E^{GEN}) / Median(E / E^{GEN})'
    elif '_E_overGEN_RMS_' in key: _titleY = '#sigma(E / E^{GEN})'
    elif '_E_GENoverREC_Mean_' in key: _titleY = '<E^{GEN} / E>'
    elif '_E_GENoverREC_RMSOverMean_' in key: _titleY = '#sigma(E^{GEN} / E) / <E^{GEN} / E>'
    elif '_E_GENoverREC_Median_' in key: _titleY = 'Median(E^{GEN} / E)'
    elif '_E_GENoverREC_RMSOverMedian_' in key: _titleY = '#sigma(E^{GEN} / E) / Median(E^{GEN} / E)'
    elif '_E_GENoverREC_RMS_' in key: _titleY = '#sigma(E^{GEN} / E)'
    elif '_pt_overGEN_Mean_' in key: _titleY = '<p_{T} / p_{T}^{GEN}>'
    elif '_pt_overGEN_RMSOverMean_' in key: _titleY = '#sigma(p_{T} / p_{T}^{GEN}) / <p_{T} / p_{T}^{GEN}>'
    elif '_pt_overGEN_Median_' in key: _titleY = 'Median(p_{T} / p_{T}^{GEN})'
    elif '_pt_overGEN_RMSOverMedian_' in key: _titleY = '#sigma(p_{T} / p_{T}^{GEN}) / Median(p_{T} / p_{T}^{GEN})'
    elif '_pt_overGEN_RMS_' in key: _titleY = '#sigma(p_{T} / p_{T}^{GEN})'
    elif '_pt_GENoverREC_Mean_' in key: _titleY = '<p_{T}^{GEN} / p_{T}>'
    elif '_pt_GENoverREC_RMSOverMean_' in key: _titleY = '#sigma(p_{T}^{GEN} / p_{T}) / <p_{T}^{GEN} / p_{T}>'
    elif '_pt_GENoverREC_Median_' in key: _titleY = 'Median(p_{T}^{GEN} / p_{T})'
    elif '_pt_GENoverREC_RMSOverMedian_' in key: _titleY = '#sigma(p_{T}^{GEN} / p_{T}) / Median(p_{T}^{GEN} / p_{T})'
    elif '_pt_GENoverREC_RMS_' in key: _titleY = '#sigma(p_{T}^{GEN} / p_{T})'
    else:
      if key.endswith('_E_overGEN'): _titleX = 'E / E^{GEN}'
      elif key.endswith('_E_GENoverREC'): _titleX = 'E^{GEN} / E'
      elif key.endswith('_E'): _titleX = 'Jet energy [GeV]'
      elif key.endswith('_pt_overGEN'): _titleX = 'p_{T} / p_{T}^{GEN}'
      elif key.endswith('_pt_GENoverREC'): _titleX = 'p_{T}^{GEN} / p_{T}'
      elif key.endswith('_pt'): _titleX = 'Jet p_{T} [GeV]'
      elif key.endswith('_eta'): _titleX = 'Jet #eta'
      elif key.endswith('_nPU'): _titleX = 'N_{PU}'
      elif key.endswith('_nCT'): _titleX = 'N_{CT}'
      elif key.endswith('_nCTie4'): _titleX = 'N_{CTie4}'

    return _titleX, _titleY, _jetLabel, _selLabel

class PlotConfig:
    def __init__(self):
        self.hists = []
        self.IsProfile = False
        self.IsEfficiency = False
        self.addLogX = False
        self.logX = False
        self.logY = False
        self.titleX = ''
        self.titleY = ''
        self.jetLabel = ''
        self.selLabel = ''
        self.legXY = [0.75, 0.60, 0.95, 0.90]
        self.legNColumns = 1
        self.xMin = None
        self.xMax = None
        self.xMinFit = None
        self.xMaxFit = None
        self.yMinRatio = None
        self.yMaxRatio = None
        self.ratio = True
        self.autoRangeX = True
        self.xLabelSize = None
        self.xBinLabels= []
        self.outputName = 'tmp'

def getHistogram(key, inputDict, plotCfg, **kwargs):

    Legend      = kwargs.get('Legend'     , inputDict['Legend'])
    Color       = kwargs.get('Color'      , inputDict['LineColor'])
    LineWidth   = kwargs.get('LineStyle'  , 2)
    LineStyle   = kwargs.get('LineStyle'  , inputDict['LineStyle'])
    MarkerStyle = kwargs.get('MarkerStyle', inputDict['MarkerStyle'])
    MarkerSize  = kwargs.get('MarkerSize' , inputDict['MarkerSize'])

    if key not in inputDict['TH1s']:
       return None

    h0 = inputDict['TH1s'][key].Clone()

    if h0.InheritsFrom('TH2'):
       return None

    h0.UseCurrentStyle()
    if hasattr(h0, 'SetDirectory'):
       h0.SetDirectory(0)

    h0.SetLineColor(Color)
    h0.SetLineWidth(2)
    h0.SetLineStyle(1 if (plotCfg.IsProfile or plotCfg.IsEfficiency) else LineStyle)
    h0.SetMarkerStyle(MarkerStyle)
    h0.SetMarkerColor(Color)
    h0.SetMarkerSize(MarkerSize if (plotCfg.IsProfile or plotCfg.IsEfficiency) else 0.)

    h0.SetBit(ROOT.TH1.kNoTitle)

    if hasattr(h0, 'SetStats'):
       h0.SetStats(0)

    hist0 = Histogram()
    hist0.th1 = h0
    hist0.draw = 'ep' if (plotCfg.IsProfile or plotCfg.IsEfficiency) else 'hist,e0'
    hist0.draw += ',same'
    hist0.Legend = Legend
    hist0.LegendDraw = 'ep' if (plotCfg.IsProfile or plotCfg.IsEfficiency) else 'l'

    return hist0

def getPlotConfig(key, keyword, inputList):

    cfg = PlotConfig()

    key_basename = os.path.basename(key)
    key_dirname = os.path.dirname(key)

    cfg.outputName = key

    cfg.IsProfile = '_wrt_' in key_basename

    cfg.IsEfficiency = key_basename.endswith('_eff')

    cfg.logY = ('_NotMatchedTo' in key_basename) and key_basename.endswith('pt_eff')

    cfg.titleX, cfg.titleY, cfg.jetLabel, cfg.selLabel = getPlotLabels(key=key_basename, keyword=keyword)

    cfg.hists = []

    if keyword == 'l1s_run3_jecFits':

       cfg.addLogX = True

       cfg.autoRangeX = False
       cfg.xMin = 1
       cfg.xMax = 3000
       cfg.xMinFit = 1
       cfg.xMaxFit = 400

       cfg.yMin = -1.1
       cfg.yMax = 4.4
       cfg.yMinRatio = 0.81
       cfg.yMaxRatio = 1.19

       cfg.doFit = False #key_basename.endswith('pt_GENoverREC_Median_wrt_pt')
       cfg.ratio = cfg.doFit

       hcolor = ROOT.kBlack
       if 'nCTie4'+'010' in key:
           hcolor = ROOT.kGreen+2
       elif 'nCTie4'+'020' in key:
           hcolor = ROOT.kBlue
       elif 'nCTie4'+'030' in key:
           hcolor = ROOT.kPink+1
       elif 'nCTie4'+'040' in key:
           hcolor = ROOT.kViolet+1
       elif 'nCTie4'+'060' in key:
           hcolor = ROOT.kOrange+2
       elif 'nCTie4'+'080' in key:
           hcolor = ROOT.kRed

       key_basename = os.path.basename(key)

       if key_basename.split('_')[0] in ['L1EmulAK4CTJet0', 'L1EmulAK4CTJet0CorrA', 'L1EmulAK4CTJet0Corr']:
           for idx, inp in enumerate(inputList):
               cfg.hists += [getHistogram(plotCfg=cfg, inputDict=inp, key=key, Legend='', Color=hcolor)]

    ##
    ## Unknown keywords
    ##
    else:
       KILL('getPlotConfig(key="'+key+'", keyword="'+keyword+'") -- invalid keyword: "'+keyword+'"')

    # remove None entries
    cfg.hists = list(filter(None, cfg.hists))

    if len(cfg.hists) < 1:
       return None

    return cfg

#### main
if __name__ == '__main__':
   ### args --------------
   parser = argparse.ArgumentParser()

   parser.add_argument('-i', '--inputs', dest='inputs', nargs='+', default=[], required=True,
                       help='list of input files [format: "PATH:LEGEND:LINECOLOR:LINESTYLE:MARKERSTYLE:MARKERCOLOR:MARKERSIZE"]')

   parser.add_argument('-o', '--output', dest='output', action='store', default=None, required=True,
                       help='path to output directory')

   parser.add_argument('-k', '--keywords', dest='keywords', nargs='+', default=[], required=True,
                       help='keywords for plot configuration')

   parser.add_argument('-m', '--matches', dest='matches', nargs='+', default=[],
                       help='list of matching-patterns to skim input histograms (input is a match if its name matches any of the specified patterns)')

   parser.add_argument('-s', '--skip', dest='skip', nargs='+', default=[],
                       help='list of matching-patterns to skip input histograms (input is skipped if its name matches any of the specified patterns)')

   parser.add_argument('-l', '--label-sample', dest='label_sample', action='store', default='',
                       help='Plot label to identify the input sample')

   parser.add_argument('-e', '--exts', dest='exts', nargs='+', default=['pdf'],
                       help='list of extension(s) for output file(s)')

   parser.add_argument('-v', '--verbosity', dest='verbosity', nargs='?', const=1, type=int, default=0,
                       help='verbosity level')

   opts, opts_unknown = parser.parse_known_args()
   ### -------------------

   ROOT.gROOT.SetBatch()
   ROOT.gErrorIgnoreLevel = ROOT.kWarning

   log_prx = os.path.basename(__file__)+' -- '

   ### args validation ---
   if len(opts_unknown) > 0:
      KILL(log_prx+'unrecognized command-line arguments: '+str(opts_unknown))

   if os.path.exists(opts.output):
      KILL(log_prx+'target path to output directory already exists [-o]: '+opts.output)

   OUTDIR = os.path.abspath(os.path.realpath(opts.output))

   KEYWORDS = sorted(list(set(opts.keywords)))

   MATCHES = sorted(list(set(opts.matches)))
   MATCHES = [_tmp.replace('\'','').replace('"','') for _tmp in MATCHES]

   SKIP = sorted(list(set(opts.skip)))
   SKIP = [_tmp.replace('\'','').replace('"','') for _tmp in SKIP]

   EXTS = list(set(opts.exts))
   ### -------------------

   inputList = []
   th1Keys = []
   for _input in opts.inputs:
       _input_pieces = _input.split(':')
       if len(_input_pieces) >= 1:
          print('reading..', os.path.relpath(_input_pieces[0]))
          _tmp = {}
          _tmp['TH1s'] = getTH1sFromTFile(_input_pieces[0], matches=MATCHES, skip=SKIP, verbose=(opts.verbosity > 20))
          th1Keys += _tmp['TH1s'].keys()
          _tmp['Legend'] = _input_pieces[1] if len(_input_pieces) >= 2 else ''
          _tmp['LineColor'] = int(_input_pieces[2]) if len(_input_pieces) >= 3 else 1
          _tmp['LineStyle'] = int(_input_pieces[3]) if len(_input_pieces) >= 4 else 1
          _tmp['MarkerStyle'] = int(_input_pieces[4]) if len(_input_pieces) >= 5 else 20
          _tmp['MarkerColor'] = int(_input_pieces[5]) if len(_input_pieces) >= 6 else _tmp['LineColor']
          _tmp['MarkerSize'] = float(_input_pieces[6]) if len(_input_pieces) >= 7 else 1.0
          inputList.append(_tmp)
       else:
          KILL(log_prx+'argument of --inputs has invalid format: '+_input)

   if not inputList:
      raise SystemExit(0)

   th1Keys = sorted(list(set(th1Keys)))

   theStyle = get_style(0)
   theStyle.cd()

   ROOT.TGaxis.SetMaxDigits(4)

   Top = ROOT.gStyle.GetPadTopMargin()
   Rig = ROOT.gStyle.GetPadRightMargin()
   Bot = ROOT.gStyle.GetPadBottomMargin()
   Lef = ROOT.gStyle.GetPadLeftMargin()

   ROOT.TGaxis.SetExponentOffset(-Lef+.50*Lef, 0.03, 'y')

   jecOutputLinesDict = {}

   for _hkey in th1Keys:
       for _keyw in KEYWORDS:
           _plotConfig = getPlotConfig(key=_hkey, keyword=_keyw, inputList=inputList)
           if _plotConfig is None:
               continue

           ## plot
           fitf = fitAndPlot(**{
             'histograms': _plotConfig.hists,
             'title': ';'+_plotConfig.titleX+';'+_plotConfig.titleY,
             'labels': [f'Sample: {opts.label_sample}', f'Jets: {_plotConfig.jetLabel}', f'Selection: {_plotConfig.selLabel}'],
             'legXY': [],
             'legNColumns': _plotConfig.legNColumns,
             'outputs': [OUTDIR+'/'+_plotConfig.outputName+'.'+_tmp for _tmp in EXTS],
             'addLogX': _plotConfig.addLogX,
             'ratio': _plotConfig.ratio,
             'logX': _plotConfig.logX,
             'logY': _plotConfig.logY,
             'xMin': _plotConfig.xMin,
             'xMax': _plotConfig.xMax,
             'doFit': _plotConfig.doFit,
             'xMinFit': _plotConfig.xMinFit,
             'xMaxFit': _plotConfig.xMaxFit,
             'yMin': _plotConfig.yMin,
             'yMax': _plotConfig.yMax,
             'yMinRatio': _plotConfig.yMinRatio,
             'yMaxRatio': _plotConfig.yMaxRatio,
             'autoRangeX': _plotConfig.autoRangeX,
             'xLabelSize': _plotConfig.xLabelSize,
             'xBinLabels': _plotConfig.xBinLabels,
           })

           if fitf is None:
               continue

           key_basename = os.path.basename(_hkey)
           key_dirname = os.path.dirname(_hkey)
           jecKey = '_'.join([key_dirname.replace('/', '_'), key_basename.split('_')[0]])

           if jecKey not in jecOutputLinesDict:
               jecOutputLinesDict[jecKey] = []

           jec_str = ''
           jec_str += f'{_plotConfig.xMinFit: 5.1f} '
           jec_str += f'{_plotConfig.xMaxFit: 5.1f} '

           sel_match = re.match('.*_eta(\+|-)(\w+)to(\+|-)(\w+)nCTie4(\d+)to(\d+?|Inf)_.*', key_basename)
           jec_str += f'{sel_match.group(1)}'
           jec_str += f'{float(sel_match.group(2).replace("p", ".")): 5.3f} '
           jec_str += f'{sel_match.group(3)}'
           jec_str += f'{float(sel_match.group(4).replace("p", ".")): 5.3f} '
           jec_str += f'{int(sel_match.group(5)): 4d} '
           jec_val4 = -1 if sel_match.group(6) == 'Inf' else int(sel_match.group(6))
           jec_str += f'{jec_val4: 4d} '

           jec_str += f'{fitf.GetFormula().GetTitle():>50} '
           jec_str += f'{fitf.GetNpar(): 3d}'
           for parIdx in range(fitf.GetNpar()):
               jec_str += f' {fitf.GetParameter(parIdx): >8.5f}'

           jecOutputLinesDict[jecKey] += [jec_str]

   for jecKey in jecOutputLinesDict:
       with open(f'{OUTDIR}/fits_{jecKey}.txt', 'w') as ofile:
           for line in jecOutputLinesDict[jecKey]:
               ofile.write(f'{line}\n')
