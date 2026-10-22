#!/usr/bin/env python3
"""
Z'->qq signal modelling.

Step 1: fit the invariant-mass histogram of each mass hypothesis (200, 300, 400,
        500 GeV) with a RooCrystalBall (double-sided, single sigma; extended, so the
        yield is fitted too),
        in the window [max(150, M/2), 700] GeV, and plot data + fit + pull.
Step 2: plot every fit parameter (mean, sigma, alphaL, nL, alphaR, nR, nsig) as
        a function of the mass hypothesis and fit it with a polynomial in mass.
        The polynomial order is either fixed or chosen automatically ('auto':
        the lowest order whose fit has a p-value above 5%), or replaced by a natural
        cubic spline through the points ('spline').
Background: the histogram whose name ends with 'data_obs' (observed data) is fitted
        with several candidate functions (exponential, power law, 'dijet' functions with
        2/3/4 parameters, exponential of a 2nd/3rd-order polynomial) in the analysis window
        [xmin_floor, xmax]. The Poisson-likelihood chi2 of each fit gives a p-value; the
        function with the largest p-value is selected, and the script stops with an error
        if none reaches p > 5%. The selected pdf is stored in the same RooWorkspace as the
        signal model (bkg_pdf, extended bkg_model with yield nbkg).
        The observable mjj spans the analysis window for signal and background alike, so
        nsig and nbkg are the expected yields in that window.
Step 3: build the resulting analytic signal model
            signal_model(mjj | mZp) = ExtendedCrystalBall(mjj; mean(mZp), sigma(mZp),
                                       alphaL(mZp), nL(mZp), alphaR(mZp), nR(mZp))
                                       with yield nsig(mZp)
        and save it as a RooWorkspace (signal_model.root) and as JSON
        (signal_parametrization.json). A validation plot overlays the model at
        the fitted masses and at the mid-points in between.

Usage:
    python fit_zprime.py input.root
    python fit_zprime.py input.root --hists h_m200 h_m300 h_m400 h_m500
    python fit_zprime.py input.root -o outdir --formats png pdf
    python fit_zprime.py input.root --default-degree auto
    python fit_zprime.py input.root --default-degree 1 --degree sigma=auto nsig=2
    python fit_zprime.py input.root --default-degree auto --degree nL=spline nR=spline
    python fit_zprime.py input.root --xmin-floor 150 --xmax 700
    python fit_zprime.py input.root --data-obs h_data_obs --bkg-functions exp dijet3 exppol2
    python fit_zprime.py input.root --skip-background      # signal model only

If --hists is not given, all TH1 objects in the file are discovered and the
mass hypothesis is parsed from each name (200/300/400/500). If a name does not
contain one of those numbers, histograms are assigned to masses in the order
they are found in the file.
"""
import argparse
import bisect
import json
import math
import re
import sys
from array import array
from pathlib import Path

import ROOT

MASSES = [200, 300, 400, 500]
DATA_OBS_SUFFIX = "data_obs"  # name suffix of the observed-data histogram
BKG_FUNCTIONS = ["exp", "power", "dijet2", "dijet3", "dijet4", "exppol2", "exppol3", "modexp"]

# Parameters that get parametrised vs. mass: name -> (axis title, unit-aware label)
PARAMS = {
    "mean": "mean [GeV]",
    "sigma": "#sigma [GeV]",
    "alphaL": "#alpha_{L}",
    "nL": "n_{L}",
    "alphaR": "#alpha_{R}",
    "nR": "n_{R}",
    "nsig": "N_{sig} (fitted yield)",
}


# --------------------------------------------------------------------------- #
# Input handling
# --------------------------------------------------------------------------- #
def load_histograms(tfile, names=None):
    """Return {mass: TH1} (histograms detached from the file)."""
    if names:
        objs = []
        for n in names:
            h = tfile.Get(n)
            if not h or not h.InheritsFrom("TH1"):
                sys.exit(f"ERROR: histogram '{n}' not found in {tfile.GetName()}")
            objs.append(h)
    else:
        objs = []
        for key in tfile.GetListOfKeys():
            if key.GetName().endswith(DATA_OBS_SUFFIX):
                continue  # observed data: handled by load_data_obs
            obj = key.ReadObj()
            if obj.InheritsFrom("TH1"):
                objs.append(obj)
        if len(objs) != len(MASSES):
            print(f"WARNING: found {len(objs)} histograms, expected {len(MASSES)}",
                  file=sys.stderr)

    result = {}
    unmatched = []
    for h in objs:
        m = re.search(r"(?<!\d)(%s)(?!\d)" % "|".join(map(str, MASSES)), h.GetName())
        if m and int(m.group(1)) not in result:
            result[int(m.group(1))] = h
        else:
            unmatched.append(h)

    # Fall back to file order for anything we could not identify from the name
    free_masses = [m for m in MASSES if m not in result]
    for m, h in zip(free_masses, unmatched):
        print(f"WARNING: could not infer mass from '{h.GetName()}', "
              f"assigning it to {m} GeV by order", file=sys.stderr)
        result[m] = h

    for h in result.values():
        h.SetDirectory(0)
    return dict(sorted(result.items()))


def load_data_obs(tfile, name=None):
    """The observed-data histogram: `name`, or the unique TH1 whose name ends with 'data_obs'."""
    if name:
        h = tfile.Get(name)
        if not h or not h.InheritsFrom("TH1"):
            sys.exit(f"ERROR: histogram '{name}' not found in {tfile.GetName()}")
    else:
        names = []
        for key in tfile.GetListOfKeys():
            if key.GetName().endswith(DATA_OBS_SUFFIX) and key.GetName() not in names \
                    and tfile.Get(key.GetName()).InheritsFrom("TH1"):
                names.append(key.GetName())
        if not names:
            sys.exit(f"ERROR: no histogram whose name ends with '{DATA_OBS_SUFFIX}' in "
                     f"{tfile.GetName()} (use --data-obs NAME, or --skip-background)")
        if len(names) > 1:
            sys.exit(f"ERROR: several histograms end with '{DATA_OBS_SUFFIX}' ({', '.join(names)}); "
                     "choose one with --data-obs NAME")
        h = tfile.Get(names[0])
    h.SetDirectory(0)
    return h


# --------------------------------------------------------------------------- #
# Step 1: fit each mass point
# --------------------------------------------------------------------------- #
def is_weighted(hist):
    """True if the bin errors differ from sqrt(content), i.e. the histogram is weighted."""
    if hist.GetSumw2N() == 0:
        return False
    for i in range(1, hist.GetNbinsX() + 1):
        content = hist.GetBinContent(i)
        if abs(hist.GetBinError(i) ** 2 - content) > 1e-6 * max(1.0, abs(content)):
            return True
    return False


def fit_window(hist, mass, xmin_floor, xmax_ceiling):
    """Fit window [max(xmin_floor, mass/2), xmax_ceiling], clipped to the histogram axis.

    Returns (lo, hi, first_bin, last_bin, n_bins). A bin belongs to the window if its
    centre lies inside it, which is how RooFit treats ranges for binned data.
    """
    ax = hist.GetXaxis()
    lo = xmin_floor #!! max(xmin_floor, 0.5 * mass)
    hi = xmax_ceiling
    if lo < ax.GetXmin() or hi > ax.GetXmax():
        print(f"WARNING: fit window [{lo:g}, {hi:g}] GeV exceeds the axis range "
              f"[{ax.GetXmin():g}, {ax.GetXmax():g}] of '{hist.GetName()}'; clipping",
              file=sys.stderr)
        lo, hi = max(lo, ax.GetXmin()), min(hi, ax.GetXmax())

    nb = hist.GetNbinsX()
    inside = [i for i in range(1, nb + 1) if lo <= ax.GetBinCenter(i) <= hi]
    if not inside:
        sys.exit(f"ERROR: no bins of '{hist.GetName()}' inside the fit window [{lo:g}, {hi:g}]")

    edges = [ax.GetBinLowEdge(i) for i in range(1, nb + 1)] + [ax.GetXmax()]
    tol = 1e-6 * (ax.GetXmax() - ax.GetXmin())
    for edge in (lo, hi):
        if min(abs(e - edge) for e in edges) > tol:
            print(f"WARNING: fit-window edge {edge:g} GeV is not a bin edge of "
                  f"'{hist.GetName()}'; bins are selected by their centre, so the "
                  f"effective window is [{ax.GetBinLowEdge(inside[0]):g}, "
                  f"{ax.GetBinUpEdge(inside[-1]):g}] GeV", file=sys.stderr)
    return lo, hi, inside[0], inside[-1], len(inside)


def slice_histogram(hist, xmin_floor, xmax_ceiling):
    """Copy of the bins of `hist` inside the analysis window [xmin_floor, xmax_ceiling]
    (bins are selected by their centre), as a new histogram detached from any file.
    Bin errors (Sumw2) are preserved."""
    lo, hi, first, last, nbins = fit_window(hist, 0.0, xmin_floor, xmax_ceiling)
    ax = hist.GetXaxis()
    edges = [ax.GetBinLowEdge(i) for i in range(first, last + 1)] + [ax.GetBinUpEdge(last)]
    out = ROOT.TH1D(f"{hist.GetName()}_window", hist.GetTitle(), nbins, array("d", edges))
    out.SetDirectory(0)
    has_sumw2 = hist.GetSumw2N() > 0
    if has_sumw2:
        out.Sumw2()
    for j, i in enumerate(range(first, last + 1), start=1):
        out.SetBinContent(j, hist.GetBinContent(i))
        if has_sumw2:
            out.SetBinError(j, hist.GetBinError(i))
    return out


def fit_histogram(hist, mass, error_mode="auto", xmin_floor=150.0, xmax_ceiling=700.0):
    """Fit one histogram; return a dict with all RooFit objects (kept alive).

    error_mode: 'auto'       -> 'sumw2' for weighted histograms, 'poisson' otherwise
                'poisson'    -> default Hesse errors (only correct for unweighted data)
                'sumw2'      -> SumW2Error(True): sandwich-corrected errors for weighted data
                'asymptotic' -> AsymptoticError(True): preferred when bins have low stats

    The fit is performed in [max(xmin_floor, mass/2), xmax_ceiling]. The observable spans the
    whole analysis window [xmin_floor, xmax_ceiling] for every mass, so nsig is the yield in
    that window (the model extrapolates it below the fit window) and has the same meaning
    for all masses.
    """
    weighted = is_weighted(hist)
    if error_mode == "auto":
        error_mode = "sumw2" if weighted else "poisson"

    hist = slice_histogram(hist, xmin_floor, xmax_ceiling)  # analysis window only
    xmin = hist.GetXaxis().GetXmin()
    xmax = hist.GetXaxis().GetXmax()
    nevt = hist.Integral()

    fit_lo, fit_hi, first_bin, last_bin, nbins_fit = fit_window(hist, mass, xmin, xmax)

    # Starting values from the histogram content inside the fit window
    hist.GetXaxis().SetRange(first_bin, last_bin)
    peak = hist.GetBinCenter(hist.GetMaximumBin())
    sigma0 = max(0.5 * hist.GetRMS(), 0.01 * peak)
    hist.GetXaxis().SetRange(0, 0)  # restore the full axis range

    tag = f"m{mass}"
    x = ROOT.RooRealVar(f"x_{tag}", "m_{jj} [GeV]", xmin, xmax)
    x.setBins(hist.GetNbinsX())
    x.setRange("fit", fit_lo, fit_hi)

    mean = ROOT.RooRealVar(f"mean_{tag}", "mean", peak, 0.8 * peak, 1.2 * peak)
    sigma = ROOT.RooRealVar(f"sigma_{tag}", "sigma", sigma0, 0.1 * sigma0, 5.0 * sigma0)
    alphaL = ROOT.RooRealVar(f"alphaL_{tag}", "alphaL", 1.5, 0.1, 10.0)
    nL = ROOT.RooRealVar(f"nL_{tag}", "nL", 5.0, 0.5, 100.0)
    alphaR = ROOT.RooRealVar(f"alphaR_{tag}", "alphaR", 1.5, 0.1, 10.0)
    nR = ROOT.RooRealVar(f"nR_{tag}", "nR", 5.0, 0.5, 100.0)

    # RooCrystalBall(name, title, x, x0, sigma, alphaL, nL, alphaR, nR): double-sided, common sigma
    pdf = ROOT.RooCrystalBall(f"cb_{tag}", "Double-sided Crystal Ball",
                              x, mean, sigma, alphaL, nL, alphaR, nR)

    # Extended pdf so that the normalisation is fitted too
    nsig = ROOT.RooRealVar(f"nsig_{tag}", "N_{sig}", nevt, 0.0, 10.0 * max(nevt, 1.0))
    model = ROOT.RooExtendPdf(f"model_{tag}", "model", pdf, nsig)

    data = ROOT.RooDataHist(f"data_{tag}", "data", ROOT.RooArgList(x), hist)

    fit_opts = [ROOT.RooFit.Save(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Strategy(2),
                ROOT.RooFit.Range("fit")]
    if error_mode == "sumw2":
        fit_opts.append(ROOT.RooFit.SumW2Error(True))
    elif error_mode == "asymptotic":
        fit_opts.append(ROOT.RooFit.AsymptoticError(True))
    result = model.fitTo(data, *fit_opts)

    return dict(x=x, mean=mean, sigma=sigma, alphaL=alphaL, nL=nL, alphaR=alphaR,
                nR=nR, pdf=pdf, nsig=nsig, model=model, data=data, result=result,
                xmin=xmin, xmax=xmax, nbins=hist.GetNbinsX(),
                fit_lo=fit_lo, fit_hi=fit_hi, nbins_fit=nbins_fit,
                weighted=weighted, error_mode=error_mode)


def print_fit_result(title, fit):
    res = fit["result"]
    line = "=" * 70
    print(f"\n{line}\nFit results for {title}\n{line}")
    print(f"  status = {res.status()}   covQual = {res.covQual()}   "
          f"minNLL = {res.minNll():.6f}   EDM = {res.edm():.3e}")
    print(f"  fit range = [{fit['fit_lo']:g}, {fit['fit_hi']:g}] GeV ({fit['nbins_fit']} bins)")
    print(f"  weighted histogram: {fit['weighted']}   parameter-error mode: {fit['error_mode']}")
    print(f"  {'parameter':<12s} {'value':>14s}   {'uncertainty':>14s}")
    for p in res.floatParsFinal():
        span = p.getMax() - p.getMin()
        at_limit = (p.getVal() - p.getMin() < 1e-3 * span
                    or p.getMax() - p.getVal() < 1e-3 * span)
        flag = "   <-- AT PARAMETER LIMIT" if at_limit else ""
        print(f"  {p.GetName():<12s} {p.getVal():>14.6g} +/- {p.getError():<14.6g}{flag}")
    const_pars = res.constPars()
    if const_pars.getSize():
        print("  Constant parameters:")
        for p in const_pars:
            print(f"  {p.GetName():<12s} {p.getVal():>14.6g}   (fixed)")
    if fit.get("ndf"):
        ptxt = f"   p-value = {fit['pvalue']:.4g}" if fit.get("pvalue") is not None else ""
        print(f"  chi2/ndf = {fit['chi2']:.3f} / {fit['ndf']}  "
              f"(= {fit['chi2'] / fit['ndf']:.3f}){ptxt}")


def make_plot(mass, fit, outdir, formats):
    x = fit["x"]
    data, model, res = fit["data"], fit["model"], fit["result"]
    n_float = res.floatParsFinal().getSize()

    # Main frame: data + fit
    fit_lo, fit_hi, nb_fit = fit["fit_lo"], fit["fit_hi"], fit["nbins_fit"]
    frame = x.frame(ROOT.RooFit.Title(" "), ROOT.RooFit.Range(fit_lo, fit_hi),
                    ROOT.RooFit.Bins(nb_fit))
    # Weighted histograms: error bars must be sqrt(sum w^2), not Poisson sqrt(sum w).
    # The pull and chi2 below use these same errors.
    data_error = ROOT.RooAbsData.SumW2 if fit["weighted"] else ROOT.RooAbsData.Poisson
    data.plotOn(frame, ROOT.RooFit.Name("data"), ROOT.RooFit.DataError(data_error))
    model.plotOn(frame, ROOT.RooFit.Name("fit"),
                 ROOT.RooFit.Range("fit"), ROOT.RooFit.NormRange("fit"),
                 ROOT.RooFit.LineColor(ROOT.kRed + 1), ROOT.RooFit.LineWidth(2))

    # chi2/ndf and pulls (must be computed after the model has been plotted)
    ndf = frame.GetNbinsX() - n_float
    chi2 = frame.chiSquare("fit", "data", n_float) * ndf
    fit["chi2"], fit["ndf"] = chi2, ndf

    pull_hist = frame.pullHist("data", "fit")
    pull_frame = x.frame(ROOT.RooFit.Title(" "), ROOT.RooFit.Range(fit_lo, fit_hi),
                         ROOT.RooFit.Bins(nb_fit))
    pull_frame.addPlotable(pull_hist, "P")

    # Canvas with two pads
    canvas = ROOT.TCanvas(f"c_{mass}", f"Z' {mass} GeV", 800, 800)
    pad_top = ROOT.TPad(f"pt_{mass}", "", 0.0, 0.30, 1.0, 1.0)
    pad_bot = ROOT.TPad(f"pb_{mass}", "", 0.0, 0.00, 1.0, 0.30)
    pad_top.SetBottomMargin(0.02)
    pad_top.SetLeftMargin(0.14)
    pad_bot.SetTopMargin(0.03)
    pad_bot.SetBottomMargin(0.35)
    pad_bot.SetLeftMargin(0.14)
    pad_bot.SetGridy(True)
    pad_top.Draw()
    pad_bot.Draw()

    # --- top pad
    pad_top.cd()
    frame.GetXaxis().SetLabelSize(0)
    frame.GetXaxis().SetTitleSize(0)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetYaxis().SetLabelSize(0.045)
    frame.GetYaxis().SetTitleOffset(1.3)
    frame.SetMinimum(0)
    frame.Draw()

    legend = ROOT.TLegend(0.62, 0.78, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(frame.findObject("data"), "Signal MC", "lep")
    legend.AddEntry(frame.findObject("fit"), "CrystalBall fit", "l")
    legend.Draw()

    # Parameter box
    box = ROOT.TPaveText(0.62, 0.40, 0.88, 0.76, "NDC")
    box.SetBorderSize(0)
    box.SetFillStyle(0)
    box.SetTextAlign(12)
    box.SetTextSize(0.033)
    box.AddText(f"m_{{Z'}} = {mass} GeV")
    for name in ("mean", "sigma", "alphaL", "nL", "alphaR", "nR"):
        p = fit[name]
        box.AddText(f"{name} = {p.getVal():.4g} #pm {p.getError():.2g}")
    box.AddText(f"#chi^{{2}}/ndf = {chi2:.1f}/{ndf}")
    box.Draw()

    # --- bottom pad (pull)
    pad_bot.cd()
    pull_frame.GetYaxis().SetTitle("Pull")
    pull_frame.GetYaxis().SetNdivisions(505)
    pull_frame.GetYaxis().SetRangeUser(-5, 5)
    pull_frame.GetYaxis().SetTitleSize(0.13)
    pull_frame.GetYaxis().SetLabelSize(0.11)
    pull_frame.GetYaxis().SetTitleOffset(0.45)
    pull_frame.GetXaxis().SetTitleSize(0.14)
    pull_frame.GetXaxis().SetLabelSize(0.11)
    pull_frame.GetXaxis().SetTitleOffset(1.0)
    pull_frame.Draw()
    line = ROOT.TLine(fit_lo, 0, fit_hi, 0)
    line.SetLineStyle(2)
    line.Draw()

    canvas.Update()
    for fmt in formats:
        canvas.SaveAs(str(outdir / f"fit_zprime_m{mass}.{fmt}"))

    # keep everything alive until the caller is done
    fit.update(frame=frame, pull_frame=pull_frame, canvas=canvas, pad_top=pad_top,
               pad_bot=pad_bot, legend=legend, box=box, line=line, pull_hist=pull_hist)


# --------------------------------------------------------------------------- #
# Step 2: fit each parameter as a function of the mass hypothesis
# --------------------------------------------------------------------------- #
def format_polynomial(name, coeffs):
    terms = []
    for i, (v, _) in enumerate(coeffs):
        if i == 0:
            terms.append(f"{v:.6g}")
        elif i == 1:
            terms.append(f"{v:+.6g}*m")
        else:
            terms.append(f"{v:+.6g}*m^{i}")
    return f"{name}(m) = " + " ".join(terms)


DEGREE_AUTO = "auto"
DEGREE_SPLINE = "spline"


def poly_fit(graph, name, degree, xlo, xhi, equal_weights):
    """Fit the graph with a polynomial of the given degree; return a result dict."""
    func = ROOT.TF1(f"f_{name}_pol{degree}", f"pol{degree}", xlo, xhi)
    opts = "SQN" + ("W" if equal_weights else "")  # save result, quiet, do not store/draw
    status = int(graph.Fit(func, opts))
    if status != 0:
        print(f"WARNING: pol{degree} fit of {name} vs mass returned status {status}",
              file=sys.stderr)
    chi2, ndf = func.GetChisquare(), func.GetNDF()
    pvalue = ROOT.TMath.Prob(chi2, ndf) if (ndf > 0 and not equal_weights) else None
    coeffs = [(func.GetParameter(i), func.GetParError(i)) for i in range(degree + 1)]
    return dict(degree=degree, func=func, coeffs=coeffs, chi2=chi2, ndf=ndf,
                pvalue=pvalue, status=status)


def fit_vs_mass(name, masses, vals, errs, degree, outdir, formats, pvalue_threshold=0.05):
    """Fit values(mass) with a polynomial and plot it.

    degree: an integer (fixed order), "auto" or "spline" (see spline_vs_mass; no fit, the
    natural cubic spline interpolates the points). With "auto", orders 0, 1, 2, ... are tried
    in turn (up to npoints-2, so that at least one degree of freedom is left for a p-value)
    and the lowest order whose fit has p-value > pvalue_threshold is used. If no order is
    acceptable, the one with the highest p-value is used and a warning is printed.
    """
    if degree == DEGREE_SPLINE:
        return spline_vs_mass(name, masses, vals, errs, outdir, formats)

    npts = len(masses)
    mlo, mhi = min(masses), max(masses)
    pad = 0.15 * (mhi - mlo)
    xlo, xhi = mlo - pad, mhi + pad

    graph = ROOT.TGraphErrors(npts, array("d", masses), array("d", vals),
                              array("d", [0.0] * npts), array("d", errs))
    graph.SetName(f"g_{name}")

    equal_weights = any(e <= 0 for e in errs)
    if equal_weights:
        print(f"WARNING: zero uncertainty on some {name} point(s); "
              "fitting with equal weights (chi2 and p-value not meaningful)", file=sys.stderr)

    scan = []
    if degree == DEGREE_AUTO:
        selection = "auto"
        if equal_weights:
            print(f"WARNING: automatic order selection needs meaningful uncertainties; "
                  f"using order {min(1, npts - 1)} for {name}", file=sys.stderr)
            chosen = poly_fit(graph, name, min(1, npts - 1), xlo, xhi, True)
        else:
            chosen, trials = None, []
            for d in range(0, npts - 1):
                trial = poly_fit(graph, name, d, xlo, xhi, False)
                trials.append(trial)
                scan.append(dict(degree=d, chi2=trial["chi2"], ndf=trial["ndf"],
                                 pvalue=trial["pvalue"]))
                if trial["pvalue"] > pvalue_threshold:
                    chosen = trial
                    break
            if chosen is None:  # nothing acceptable: fall back to the best p-value
                chosen = max(trials, key=lambda t: t["pvalue"])
            if chosen["pvalue"] <= pvalue_threshold:
                print(f"WARNING: no polynomial order gives p-value > {pvalue_threshold:g} for "
                      f"{name}; using the best one (order {chosen['degree']}, "
                      f"p = {chosen['pvalue']:.4f})", file=sys.stderr)
    else:
        selection = "fixed"
        if degree > npts - 1:
            print(f"WARNING: degree {degree} too high for {npts} points ({name}); "
                  f"using {npts - 1}", file=sys.stderr)
            degree = npts - 1
        chosen = poly_fit(graph, name, degree, xlo, xhi, equal_weights)

    degree, func, coeffs = chosen["degree"], chosen["func"], chosen["coeffs"]
    chi2, ndf, pvalue = chosen["chi2"], chosen["ndf"], chosen["pvalue"]

    # --- plot
    canvas = ROOT.TCanvas(f"c_vs_m_{name}", name, 700, 550)
    canvas.SetLeftMargin(0.16)
    canvas.SetGrid()
    graph.SetTitle("")
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.2)
    graph.Draw("AP")
    graph.GetXaxis().SetTitle("m_{Z'} hypothesis [GeV]")
    graph.GetYaxis().SetTitle(PARAMS[name])
    graph.GetYaxis().SetTitleOffset(1.5)
    func.SetLineColor(ROOT.kRed + 1)
    func.SetLineWidth(2)
    func.Draw("same")

    box = ROOT.TPaveText(0.20, 0.68, 0.60, 0.88, "NDC")
    box.SetBorderSize(0)
    box.SetFillStyle(0)
    box.SetTextAlign(12)
    box.SetTextSize(0.035)
    box.AddText(f"pol{degree} fit" + (" (auto-selected)" if selection == "auto" else ""))
    chi_txt = f"#chi^{{2}}/ndf = {chi2:.2f}/{ndf}" if ndf > 0 else "ndf = 0 (exact interpolation)"
    box.AddText(chi_txt)
    if pvalue is not None:
        box.AddText(f"p-value = {pvalue:.3f}")
    box.Draw()

    canvas.Update()
    for fmt in formats:
        canvas.SaveAs(str(outdir / f"param_{name}_vs_mass.{fmt}"))

    return dict(kind="poly", degree=degree, coeffs=coeffs, chi2=chi2, ndf=ndf, pvalue=pvalue,
                status=chosen["status"], selection=selection, scan=scan,
                graph=graph, func=func, canvas=canvas, box=box)


def natural_cubic_spline(xs, ys):
    """Natural cubic spline through the points (second derivative = 0 at both ends).

    On [xs[i], xs[i+1]) the spline is  a + b*dx + c*dx^2 + d*dx^3  with dx = x - xs[i];
    outside [xs[0], xs[-1]] it is continued linearly with the slope at the end point.
    """
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    if n < 2 or any(hi <= 0 for hi in h):
        raise ValueError("spline needs at least 2 strictly increasing knots")

    # second derivatives M[i]; natural boundary conditions M[0] = M[n-1] = 0
    M = [0.0] * n
    m = n - 2  # number of interior knots = number of unknowns
    if m > 0:
        diag = [2.0 * (h[k] + h[k + 1]) for k in range(m)]
        rhs = [6.0 * ((ys[k + 2] - ys[k + 1]) / h[k + 1] - (ys[k + 1] - ys[k]) / h[k])
               for k in range(m)]
        # Thomas algorithm for the tridiagonal system (sub-diagonal h[k], super-diagonal h[k+1])
        cp, dp = [0.0] * m, [0.0] * m
        cp[0], dp[0] = (h[1] / diag[0] if m > 1 else 0.0), rhs[0] / diag[0]
        for k in range(1, m):
            denom = diag[k] - h[k] * cp[k - 1]
            cp[k] = h[k + 1] / denom if k < m - 1 else 0.0
            dp[k] = (rhs[k] - h[k] * dp[k - 1]) / denom
        u = [0.0] * m
        u[m - 1] = dp[m - 1]
        for k in range(m - 2, -1, -1):
            u[k] = dp[k] - cp[k] * u[k + 1]
        M[1:n - 1] = u

    segments = []
    for i in range(n - 1):
        a = ys[i]
        b = (ys[i + 1] - ys[i]) / h[i] - h[i] * (2.0 * M[i] + M[i + 1]) / 6.0
        c = M[i] / 2.0
        d = (M[i + 1] - M[i]) / (6.0 * h[i])
        segments.append((a, b, c, d))

    a, b, c, d = segments[-1]
    slope_right = b + 2.0 * c * h[-1] + 3.0 * d * h[-1] ** 2
    return dict(knots=list(xs), values=list(ys), segments=segments,
                slope_left=segments[0][1], slope_right=slope_right)


def eval_spline(sp, x):
    xs = sp["knots"]
    if x <= xs[0]:
        return sp["values"][0] + sp["slope_left"] * (x - xs[0])
    if x >= xs[-1]:
        return sp["values"][-1] + sp["slope_right"] * (x - xs[-1])
    i = min(bisect.bisect_right(xs, x) - 1, len(xs) - 2)
    a, b, c, d = sp["segments"][i]
    dx = x - xs[i]
    return a + dx * (b + dx * (c + dx * d))


def spline_formula(sp, var="@0"):
    """The spline as one closed-form expression (nested ternaries), e.g. for RooFormulaVar
    (var="@0" is the first argument of the RooFormulaVar)."""
    xs, ys, segs = sp["knots"], sp["values"], sp["segments"]

    def num(v):
        return f"({v!r})"

    def segment(i):
        a, b, c, d = segs[i]
        dx = f"({var}-{num(xs[i])})"
        return f"{num(a)}+{dx}*({num(b)}+{dx}*({num(c)}+{dx}*{num(d)}))"

    expr = f"({num(ys[-1])}+{num(sp['slope_right'])}*({var}-{num(xs[-1])}))"
    for i in range(len(segs) - 1, -1, -1):
        expr = f"(({var}<{num(xs[i + 1])})?({segment(i)}):{expr})"
    left = f"{num(ys[0])}+{num(sp['slope_left'])}*({var}-{num(xs[0])})"
    return f"({var}<{num(xs[0])})?({left}):{expr}"


def spline_vs_mass(name, masses, vals, errs, outdir, formats):
    """Natural cubic spline through the fitted values of one parameter, and its plot.

    This is an interpolation: the curve passes exactly through the points, their
    uncertainties are not used, and there is no goodness-of-fit (no chi2 / p-value).
    Outside the mass range the spline is continued linearly.
    """
    npts = len(masses)
    sp = natural_cubic_spline(list(masses), list(vals))
    mlo, mhi = min(masses), max(masses)
    pad = 0.15 * (mhi - mlo)
    xlo, xhi = mlo - pad, mhi + pad

    graph = ROOT.TGraphErrors(npts, array("d", masses), array("d", vals),
                              array("d", [0.0] * npts), array("d", errs))
    graph.SetName(f"g_{name}")

    ncurve = 200
    xs_c = [xlo + (xhi - xlo) * k / (ncurve - 1) for k in range(ncurve)]
    ys_c = [eval_spline(sp, v) for v in xs_c]
    curve = ROOT.TGraph(ncurve, array("d", xs_c), array("d", ys_c))
    curve.SetName(f"spline_{name}")

    ylo = min(min(v - abs(e) for v, e in zip(vals, errs)), min(ys_c))
    yhi = max(max(v + abs(e) for v, e in zip(vals, errs)), max(ys_c))
    margin = 0.1 * (yhi - ylo) if yhi > ylo else 1.0

    canvas = ROOT.TCanvas(f"c_vs_m_{name}", name, 700, 550)
    canvas.SetLeftMargin(0.16)
    canvas.SetGrid()
    graph.SetTitle("")
    graph.SetMarkerStyle(20)
    graph.SetMarkerSize(1.2)
    graph.Draw("AP")
    graph.GetXaxis().SetTitle("m_{Z'} hypothesis [GeV]")
    graph.GetXaxis().SetLimits(xlo, xhi)
    graph.GetYaxis().SetTitle(PARAMS[name])
    graph.GetYaxis().SetTitleOffset(1.5)
    graph.GetYaxis().SetRangeUser(ylo - margin, yhi + margin)
    curve.SetLineColor(ROOT.kRed + 1)
    curve.SetLineWidth(2)
    curve.Draw("L")

    box = ROOT.TPaveText(0.20, 0.76, 0.60, 0.88, "NDC")
    box.SetBorderSize(0)
    box.SetFillStyle(0)
    box.SetTextAlign(12)
    box.SetTextSize(0.035)
    box.AddText("natural cubic spline")
    box.AddText("(interpolation, linear extrapolation)")
    box.Draw()

    canvas.Update()
    for fmt in formats:
        canvas.SaveAs(str(outdir / f"param_{name}_vs_mass.{fmt}"))

    return dict(kind="spline", degree=None, coeffs=None, chi2=None, ndf=0, pvalue=None,
                status=0, selection="spline", scan=[], spline=sp,
                expression=spline_formula(sp, "m"),
                graph=graph, curve=curve, canvas=canvas, box=box)


def print_spline(name, pf):
    sp = pf["spline"]
    xs = sp["knots"]
    print(f"\n  {name}(m): natural cubic spline through the {len(xs)} fitted values "
          f"(linear extrapolation outside [{xs[0]:g}, {xs[-1]:g}] GeV)   [spline]")
    for i, (a, b, c, d) in enumerate(sp["segments"]):
        print(f"    m in [{xs[i]:g}, {xs[i + 1]:g}):  {a:.6g} {b:+.6g}*dx {c:+.6g}*dx^2 "
              f"{d:+.6g}*dx^3,   dx = m - {xs[i]:g}")
    print("    (interpolation: the curve passes through the points; their uncertainties "
          "are not used, so there is no chi2/p-value)")


def param_to_json(name, pf):
    if pf["kind"] == "spline":
        sp = pf["spline"]
        return dict(
            kind="spline",
            spline_type="natural cubic, linear extrapolation outside the knots",
            knots=sp["knots"],
            values=sp["values"],
            segments=[dict(x0=sp["knots"][i], a=a, b=b, c=c, d=d)
                      for i, (a, b, c, d) in enumerate(sp["segments"])],
            slope_left=sp["slope_left"],
            slope_right=sp["slope_right"],
            formula=f"{name}(m) = {pf['expression']}",
        )
    return dict(
        kind="poly",
        degree=pf["degree"],
        degree_selection=pf["selection"],
        pvalue=pf["pvalue"],
        coefficients=[c for c, _ in pf["coeffs"]],
        coefficient_errors=[e for _, e in pf["coeffs"]],
        chi2=pf["chi2"],
        ndf=pf["ndf"],
        formula=format_polynomial(name, pf["coeffs"]),
    )


# --------------------------------------------------------------------------- #
# Background: fit data_obs with several functions and keep the best one
# --------------------------------------------------------------------------- #
def estimate_slopes(hist):
    """Rough log-slopes of a falling spectrum (fit starting values only):
    d ln(n)/dm for the exponentials and d ln(n)/d ln(m) for the power-law-like functions,
    from a least-squares line through the bins with n > 0."""
    pts = [(hist.GetBinCenter(i), hist.GetBinContent(i))
           for i in range(1, hist.GetNbinsX() + 1) if hist.GetBinContent(i) > 0]

    def slope(xs, ys):
        if len(xs) < 2:
            return None
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        den = sum((a - mx) ** 2 for a in xs)
        return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / den if den > 0 else None

    ms = [m for m, _ in pts]
    lnn = [math.log(n) for _, n in pts]
    exp_slope = slope(ms, lnn)
    pow_slope = slope([math.log(m) for m in ms], lnn)
    return dict(exp_slope=exp_slope if exp_slope is not None else -0.01,
                power_slope=pow_slope if pow_slope is not None else -5.0)


def build_bkg_pdf(func, x, tag, sqrts, start=None, pdf_name=None):
    """Build the candidate background pdf `func` on the observable x (a RooRealVar, in GeV).

    Returns (pdf, params, formula): params maps the parameter name (e.g. 'p1') to its
    RooRealVar (named '<name>_<tag>'); formula is a human-readable expression in m = mjj.
    Functions (X = m / sqrts, u = m / 1000 GeV):
      exp      exp(c*m)
      power    X^p1
      dijet2   (1-X)^p1 / X^p2
      dijet3   (1-X)^p1 / X^(p2 + p3*ln X)
      dijet4   (1-X)^p1 / X^(p2 + p3*ln X + p4*ln(X)^2)
      exppol2  exp(p1*u + p2*u^2)
      exppol3  exp(p1*u + p2*u^2 + p3*u^3)
      modexp   exp(p1*X^p2 + p3*(1-X)^p4)
    """
    start = start or {}
    s_exp = start.get("exp_slope", -0.01)
    s_pow = start.get("power_slope", -5.0)
    pdf_name = pdf_name or f"pdf_{tag}"
    title = f"background: {func}"
    S = repr(float(sqrts))
    params = {}

    def par(name, val, lo, hi):
        eps = 1e-6 * (hi - lo)
        val = min(max(val, lo + eps), hi - eps)  # keep the starting value inside the range
        params[name] = ROOT.RooRealVar(f"{name}_{tag}", name, val, lo, hi)
        return params[name]

    def arglist(*objs):
        lst = ROOT.RooArgList()
        for o in objs:
            lst.add(o)
        return lst

    xs = f"(@0/{S})"
    lnx = f"log({xs})"
    if func == "exp":
        c = par("c", s_exp, -1.0, 0.0)  # slope in 1/GeV
        pdf = ROOT.RooExponential(pdf_name, title, x, c)
        formula = "exp(c*m)"
    elif func == "power":
        p1 = par("p1", s_pow, -30.0, 5.0)
        pdf = ROOT.RooGenericPdf(pdf_name, title, f"pow({xs}, @1)", arglist(x, p1))
        formula = f"(m/{S})^p1"
    elif func in ("dijet2", "dijet3", "dijet4"):
        p1 = par("p1", 5.0, -50.0, 200.0)
        p2 = par("p2", -s_pow, -10.0, 40.0)
        objs, expo, form = [x, p1, p2], "@2", "p2"
        if func in ("dijet3", "dijet4"):
            objs.append(par("p3", 0.0, -10.0, 10.0))
            expo += f" + @3*{lnx}"
            form += f" + p3*ln(m/{S})"
        if func == "dijet4":
            objs.append(par("p4", 0.0, -5.0, 5.0))
            expo += f" + @4*pow({lnx}, 2)"
            form += f" + p4*ln(m/{S})^2"
        pdf = ROOT.RooGenericPdf(pdf_name, title, f"pow(1 - {xs}, @1) / pow({xs}, {expo})", arglist(*objs))
        formula = f"(1-m/{S})^p1 / (m/{S})^({form})"
    elif func in ("exppol2", "exppol3"):
        u = "(@0/1000.0)"
        objs = [x, par("p1", 1000.0 * s_exp, -300.0, 50.0), par("p2", 0.0, -300.0, 300.0)]
        expo, form = f"@1*{u} + @2*{u}*{u}", "p1*u + p2*u^2"
        if func == "exppol3":
            objs.append(par("p3", 0.0, -500.0, 500.0))
            expo += f" + @3*{u}*{u}*{u}"
            form += " + p3*u^3"
        pdf = ROOT.RooGenericPdf(pdf_name, title, f"exp({expo})", arglist(*objs))
        formula = f"exp({form}), u = m/1000"
    elif func in ("modexp"):
        p1 = par("p1", -240, -280, -120)
        p2 = par("p2", 1.12, 0.7, 3)
        p3 = par("p3", 8.8, 1, 20)
        p4 = par("p4", 140, 50, 180)
        objs = [x, p1, p2, p3, p4]
        expo = f"@1*pow({xs},@2) + @3*pow(1-{xs},@4)"
        form = f"p1*(m/{S})^p2 + p3*(1-m/{S})^p4"
        pdf = ROOT.RooGenericPdf(pdf_name, title, f"exp({expo})", arglist(*objs))
        formula = f"exp({form})"
    else:
        raise ValueError(f"unknown background function '{func}' (choose from "
                         f"{', '.join(BKG_FUNCTIONS)})")
    return pdf, params, formula


def poisson_chi2(pdf, nexp_total, x, hist):
    """Baker-Cousins (Poisson likelihood-ratio) chi2 of an extended pdf against a histogram:
    2 * sum_i [nu_i - n_i + n_i ln(n_i/nu_i)], valid also for bins with few or no entries.
    nu_i is the expectation integrated over bin i."""
    ax = hist.GetXaxis()
    norm = ROOT.RooArgSet(x)
    chi2 = 0.0
    for i in range(1, hist.GetNbinsX() + 1):
        rname = f"bin{i}_{pdf.GetName()}"
        x.setRange(rname, ax.GetBinLowEdge(i), ax.GetBinUpEdge(i))
        frac = pdf.createIntegral(norm, ROOT.RooFit.NormSet(norm),
                                  ROOT.RooFit.Range(rname)).getVal()
        nu, n = nexp_total * frac, hist.GetBinContent(i)
        if nu <= 0.0:
            if n > 0.0:
                return float("inf")
            continue
        chi2 += 2.0 * (nu - n + (n * math.log(n / nu) if n > 0.0 else 0.0))
    return chi2


def fit_background(func, hist, error_mode, sqrts, start):
    """Fit one candidate function to `hist` (extended binned fit over the whole histogram)."""
    weighted = is_weighted(hist)
    if error_mode == "auto":
        error_mode = "sumw2" if weighted else "poisson"
    tag = f"bkg_{func}"
    xmin, xmax, nbins = hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax(), hist.GetNbinsX()

    x = ROOT.RooRealVar(f"x_{tag}", "m_{jj} [GeV]", xmin, xmax)
    x.setBins(nbins)
    pdf, params, formula = build_bkg_pdf(func, x, tag, sqrts, start)
    nevt = hist.Integral()
    nbkg = ROOT.RooRealVar(f"nbkg_{tag}", "N_{bkg}", nevt, 0.0, 10.0 * max(nevt, 1.0))
    model = ROOT.RooExtendPdf(f"model_{tag}", "model", pdf, nbkg)
    data = ROOT.RooDataHist(f"data_{tag}", "data", ROOT.RooArgList(x), hist)

    # IntegrateBins: integrate the (steeply falling) pdf over each bin instead of evaluating
    # it at the bin centre
    fit_opts = [ROOT.RooFit.Save(True), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Strategy(2),
                ROOT.RooFit.IntegrateBins(1e-3)]
    if error_mode == "sumw2":
        fit_opts.append(ROOT.RooFit.SumW2Error(True))
    elif error_mode == "asymptotic":
        fit_opts.append(ROOT.RooFit.AsymptoticError(True))
    result = model.fitTo(data, *fit_opts)

    n_float = result.floatParsFinal().getSize()
    ndf = nbins - n_float
    chi2 = poisson_chi2(pdf, nbkg.getVal(), x, hist)
    pvalue = ROOT.TMath.Prob(chi2, ndf) if (ndf > 0 and math.isfinite(chi2)) else None
    converged = result.status() == 0 and math.isfinite(chi2)
    return dict(func=func, formula=formula, x=x, pdf=pdf, params=params, nbkg=nbkg,
                model=model, data=data, result=result, chi2=chi2, ndf=ndf, pvalue=pvalue,
                n_float=n_float, converged=converged, weighted=weighted,
                error_mode=error_mode, xmin=xmin, xmax=xmax, nbins_fit=nbins,
                fit_lo=xmin, fit_hi=xmax)


def print_background_table(cands):
    print(f"\n  {'function':<9s} {'npar':>4s} {'status':>6s} {'chi2/ndf':>14s} {'p-value':>11s}")
    for c in cands:
        if c.get("error"):
            print(f"  {c['func']:<9s} {'-':>4s} {'-':>6s}   FAILED: {c['error']}")
            continue
        pv = f"{c['pvalue']:.4g}" if c["pvalue"] is not None else "n/a"
        note = "" if c["converged"] else "   (not converged: excluded)"
        print(f"  {c['func']:<9s} {c['n_float']:>4d} {c['result'].status():>6d} "
              f"{c['chi2']:>9.2f}/{c['ndf']:<4d} {pv:>11s}{note}")


def make_background_plot(best, outdir, formats):
    """data_obs + selected fit (log scale) with the pull in a sub-pad."""
    x, data, model = best["x"], best["data"], best["model"]
    nb = best["nbins_fit"]
    frame = x.frame(ROOT.RooFit.Title(" "), ROOT.RooFit.Bins(nb))
    data_error = ROOT.RooAbsData.SumW2 if best["weighted"] else ROOT.RooAbsData.Poisson
    data.plotOn(frame, ROOT.RooFit.Name("data"), ROOT.RooFit.DataError(data_error))
    model.plotOn(frame, ROOT.RooFit.Name("fit"),
                 ROOT.RooFit.LineColor(ROOT.kRed + 1), ROOT.RooFit.LineWidth(2))
    pull_hist = frame.pullHist("data", "fit")
    pull_frame = x.frame(ROOT.RooFit.Title(" "), ROOT.RooFit.Bins(nb))
    pull_frame.addPlotable(pull_hist, "P")

    canvas = ROOT.TCanvas("c_background", "background fit", 800, 800)
    pad_top = ROOT.TPad("pt_bkg", "", 0.0, 0.30, 1.0, 1.0)
    pad_bot = ROOT.TPad("pb_bkg", "", 0.0, 0.00, 1.0, 0.30)
    pad_top.SetBottomMargin(0.02)
    pad_top.SetLeftMargin(0.14)
    pad_top.SetLogy(True)
    pad_bot.SetTopMargin(0.03)
    pad_bot.SetBottomMargin(0.35)
    pad_bot.SetLeftMargin(0.14)
    pad_bot.SetGridy(True)
    pad_top.Draw()
    pad_bot.Draw()

    pad_top.cd()
    frame.GetXaxis().SetLabelSize(0)
    frame.GetXaxis().SetTitleSize(0)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetYaxis().SetLabelSize(0.045)
    frame.GetYaxis().SetTitleOffset(1.3)
    frame.SetMinimum(0.5)
    frame.Draw()

    legend = ROOT.TLegend(0.60, 0.80, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(frame.findObject("data"), "data_obs", "lep")
    legend.AddEntry(frame.findObject("fit"), f"{best['func']} fit", "l")
    legend.Draw()

    box = ROOT.TPaveText(0.60, 0.45, 0.88, 0.78, "NDC")
    box.SetBorderSize(0)
    box.SetFillStyle(0)
    box.SetTextAlign(12)
    box.SetTextSize(0.033)
    for name, p in best["params"].items():
        box.AddText(f"{name} = {p.getVal():.4g} #pm {p.getError():.2g}")
    box.AddText(f"N_{{bkg}} = {best['nbkg'].getVal():.5g}")
    box.AddText(f"#chi^{{2}}/ndf = {best['chi2']:.1f}/{best['ndf']}")
    if best["pvalue"] is not None:
        box.AddText(f"p-value = {best['pvalue']:.3g}")
    box.Draw()

    pad_bot.cd()
    pull_frame.GetYaxis().SetTitle("Pull")
    pull_frame.GetYaxis().SetNdivisions(505)
    pull_frame.GetYaxis().SetRangeUser(-5, 5)
    pull_frame.GetYaxis().SetTitleSize(0.13)
    pull_frame.GetYaxis().SetLabelSize(0.11)
    pull_frame.GetYaxis().SetTitleOffset(0.45)
    pull_frame.GetXaxis().SetTitleSize(0.14)
    pull_frame.GetXaxis().SetLabelSize(0.11)
    pull_frame.GetXaxis().SetTitleOffset(1.0)
    pull_frame.Draw()
    zero = ROOT.TLine(best["xmin"], 0, best["xmax"], 0)
    zero.SetLineStyle(2)
    zero.Draw()

    canvas.Update()
    for fmt in formats:
        canvas.SaveAs(str(outdir / f"fit_background.{fmt}"))
    best.update(frame=frame, pull_frame=pull_frame, canvas=canvas, pad_top=pad_top,
                pad_bot=pad_bot, legend=legend, box=box, zero=zero, pull_hist=pull_hist)


def fit_background_functions(hist, funcs, error_mode, sqrts, threshold, outdir, formats,
                             hist_name=None):
    """Fit every candidate to `hist`, select the one with the largest p-value among the
    converged fits, and stop with an error if its p-value is not above `threshold`."""
    start = estimate_slopes(hist)
    print(f"  fit range [{hist.GetXaxis().GetXmin():g}, {hist.GetXaxis().GetXmax():g}] GeV, "
          f"{hist.GetNbinsX()} bins, {hist.Integral():.6g} events")
    if is_weighted(hist):
        print("WARNING: the data histogram looks weighted; the Poisson chi2 / p-values are "
              "only approximate for weighted entries", file=sys.stderr)

    cands = []
    for func in funcs:
        print(f"  fitting '{func}' ...")
        try:
            cands.append(fit_background(func, hist, error_mode, sqrts, start))
        except Exception as exc:  # keep going with the other candidates
            cands.append(dict(func=func, converged=False, error=str(exc), chi2=None,
                              ndf=None, pvalue=None, n_float=None))
    print_background_table(cands)

    valid = [c for c in cands if c["converged"] and c["pvalue"] is not None]
    if not valid:
        sys.exit("ERROR: none of the background fits converged with a defined p-value "
                 "(see the table above)")
    best = max(valid, key=lambda c: c["pvalue"])
    make_background_plot(best, outdir, formats)
    print_fit_result(f"background function '{best['func']}'", best)
    if best["pvalue"] <= threshold:
        sys.exit(f"ERROR: no background function reaches p-value > {threshold:g}; the best is "
                 f"'{best['func']}' with p = {best['pvalue']:.3g} (see the table above and "
                 f"fit_background.* in {outdir})")
    print(f"\n  Selected background function: '{best['func']}' "
          f"(p-value = {best['pvalue']:.4g}, threshold {threshold:g})")
    return dict(best=best, candidates=cands, hist_name=hist_name or hist.GetName())


def background_to_json(background, sqrts, threshold):
    best = background["best"]
    return dict(
        histogram=background["hist_name"],
        function=best["func"],
        formula=best["formula"],
        sqrts=sqrts,
        fit_range=[best["xmin"], best["xmax"]],
        chi2=best["chi2"],
        ndf=best["ndf"],
        pvalue=best["pvalue"],
        pvalue_threshold=threshold,
        yield_nbkg=dict(value=best["nbkg"].getVal(), error=best["nbkg"].getError()),
        parameters={n: dict(value=p.getVal(), error=p.getError())
                    for n, p in best["params"].items()},
        workspace=dict(pdf="bkg_pdf", extended_model="bkg_model", yield_="nbkg",
                       parameter_suffix="_bkg"),
        candidates=[dict(function=c["func"], n_params=c.get("n_float"),
                         converged=c["converged"], chi2=c["chi2"], ndf=c["ndf"],
                         pvalue=c["pvalue"]) for c in background["candidates"]],
    )


# --------------------------------------------------------------------------- #
# Step 3: analytic signal model
# --------------------------------------------------------------------------- #
def build_workspace(param_fits, xlo, xhi, mlo, mhi, outpath, background=None, sqrts=13600.0):
    """RooWorkspace with signal_model(mjj | mZp) built from the fitted parametrisations and,
    if `background` (the selected fit from fit_background_functions) is given, the extended
    background model bkg_model(mjj) = bkg_pdf with yield nbkg."""
    w = ROOT.RooWorkspace("w", "Z' signal and background model")
    mjj = ROOT.RooRealVar("mjj", "m_{jj} [GeV]", xlo, xhi)
    mzp = ROOT.RooRealVar("mZp", "m_{Z'} [GeV]", 0.5 * (mlo + mhi), mlo, mhi)

    keep = [mjj, mzp]
    polys = {}
    for name in PARAMS:
        if param_fits[name]["kind"] == "spline":
            expression = spline_formula(param_fits[name]["spline"], "@0")
            poly = ROOT.RooFormulaVar(f"{name}_of_m", f"{name}(m_{{Z'}})", expression,
                                      ROOT.RooArgList(mzp))
        else:
            coeff_list = ROOT.RooArgList()
            for i, (val, _) in enumerate(param_fits[name]["coeffs"]):
                c = ROOT.RooRealVar(f"{name}_c{i}", f"{name} coefficient {i}", val)
                c.setConstant(True)
                keep.append(c)
                coeff_list.add(c)
            poly = ROOT.RooPolyVar(f"{name}_of_m", f"{name}(m_{{Z'}})", mzp, coeff_list)
        keep.append(poly)
        polys[name] = poly

    pdf = ROOT.RooCrystalBall("signal_pdf", "Double-sided CB signal shape", mjj,
                              polys["mean"], polys["sigma"],
                              polys["alphaL"], polys["nL"], polys["alphaR"], polys["nR"])
    model = ROOT.RooExtendPdf("signal_model", "Extended signal model", pdf, polys["nsig"])
    getattr(w, "import")(model)
    keep += [pdf, model]

    if background is not None:
        # Rebuild the selected function on the workspace observable and set the fitted
        # values; the parameters stay floating (with their fitted errors) for later use
        bkg_pdf, bkg_params, _ = build_bkg_pdf(background["func"], mjj, "bkg", sqrts,
                                               pdf_name="bkg_pdf")
        for pname, rrv in bkg_params.items():
            fitted = background["params"][pname]
            rrv.setVal(fitted.getVal())
            rrv.setError(fitted.getError())
        nfit = background["nbkg"]
        nbkg = ROOT.RooRealVar("nbkg", "N_{bkg}", nfit.getVal(), 0.0,
                               10.0 * max(nfit.getVal(), 1.0))
        nbkg.setError(nfit.getError())
        bkg_model = ROOT.RooExtendPdf("bkg_model", "Extended background model", bkg_pdf, nbkg)
        getattr(w, "import")(bkg_model)
        keep += [bkg_pdf, nbkg, bkg_model] + list(bkg_params.values())

    w.writeToFile(str(outpath))
    return w, keep


def validation_plot(w, masses, nbins, outdir, formats):
    """Overlay the parametrised model at the fitted masses (solid) and mid-points (dashed)."""
    mjj, mzp, model = w.var("mjj"), w.var("mZp"), w.pdf("signal_model")
    mids = [0.5 * (a + b) for a, b in zip(masses[:-1], masses[1:])]
    colors = [ROOT.kBlack, ROOT.kRed + 1, ROOT.kBlue + 1, ROOT.kGreen + 2,
              ROOT.kMagenta + 1, ROOT.kOrange + 1, ROOT.kCyan + 2]

    frame = mjj.frame(ROOT.RooFit.Bins(nbins), ROOT.RooFit.Title(" "))
    entries = []
    for i, m in enumerate(sorted(masses + mids)):
        mzp.setVal(m)
        solid = m in masses
        name = f"curve_{m:g}"
        model.plotOn(frame, ROOT.RooFit.Name(name),
                     ROOT.RooFit.Normalization(1.0, ROOT.RooAbsReal.RelativeExpected),
                     ROOT.RooFit.LineColor(colors[i % len(colors)]),
                     ROOT.RooFit.LineStyle(1 if solid else 2),
                     ROOT.RooFit.LineWidth(2))
        entries.append((name, f"m_{{Z'}} = {m:g} GeV" + ("" if solid else " (interp.)")))

    canvas = ROOT.TCanvas("c_validation", "validation", 900, 600)
    canvas.SetLeftMargin(0.12)
    frame.GetYaxis().SetTitle("Events / bin")
    frame.GetYaxis().SetTitleOffset(1.3)
    frame.Draw()
    legend = ROOT.TLegend(0.68, 0.45, 0.89, 0.89)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    for name, label in entries:
        legend.AddEntry(frame.findObject(name), label, "l")
    legend.Draw()
    canvas.Update()
    for fmt in formats:
        canvas.SaveAs(str(outdir / f"signal_model_validation.{fmt}"))
    return frame, canvas, legend


# --------------------------------------------------------------------------- #
def parse_degree_value(text):
    """'auto', 'spline' or a non-negative integer (argparse type)."""
    if text.lower() in (DEGREE_AUTO, DEGREE_SPLINE):
        return text.lower()
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not an integer, 'auto' or 'spline'")
    if value < 0:
        raise argparse.ArgumentTypeError("polynomial order must be >= 0")
    return value


def parse_degrees(items, default):
    degrees = {name: default for name in PARAMS}
    for item in items or []:
        try:
            name, deg = item.split("=")
            deg = parse_degree_value(deg)
        except (ValueError, argparse.ArgumentTypeError):
            sys.exit(f"ERROR: bad --degree '{item}' (expected name=N, name=auto or name=spline)")
        if name not in PARAMS:
            sys.exit(f"ERROR: unknown parameter '{name}' (choose from {', '.join(PARAMS)})")
        degrees[name] = deg
    return degrees


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="input ROOT file")
    ap.add_argument("--hists", nargs="+", default=None,
                    help="histogram names (default: auto-discover)")
    ap.add_argument("-o", "--outdir", default=".", help="output directory")
    ap.add_argument("--formats", nargs="+", default=["png", "pdf"],
                    help="plot formats (default: png pdf)")
    ap.add_argument("--errors", choices=["auto", "poisson", "sumw2", "asymptotic"],
                    default="auto",
                    help="how to compute fit-parameter errors: 'auto' uses SumW2Error for "
                         "weighted histograms and default errors otherwise; 'asymptotic' "
                         "is preferred if some bins have very low statistics (default: auto)")
    ap.add_argument("--xmin-floor", type=float, default=150.0,
                    help="the fit window starts at max(XMIN_FLOOR, M_Z'/2) GeV (default: 150)")
    ap.add_argument("--xmax", type=float, default=700.0,
                    help="upper edge of the fit window in GeV (default: 700)")
    ap.add_argument("--default-degree", type=parse_degree_value, default=DEGREE_AUTO,
                    metavar="N|auto|spline",
                    help="model for the parameter-vs-mass fits: a polynomial order N, 'auto' = "
                         "lowest polynomial order whose fit p-value exceeds --pvalue-threshold, "
                         "or 'spline' = natural cubic spline through the points (default: auto)")
    ap.add_argument("--degree", nargs="*", default=None, metavar="NAME=N|auto|spline",
                    help=f"per-parameter override, e.g. sigma=2, nsig=auto or nL=spline "
                         f"(parameters: {', '.join(PARAMS)})")
    ap.add_argument("--pvalue-threshold", type=float, default=0.05,
                    help="minimum p-value accepted by the 'auto' order selection (default: 0.05)")
    ap.add_argument("--data-obs", default=None, metavar="NAME",
                    help="name of the observed-data histogram for the background fits "
                         f"(default: the TH1 whose name ends with '{DATA_OBS_SUFFIX}')")
    ap.add_argument("--skip-background", action="store_true",
                    help="skip the background fits (signal model only)")
    ap.add_argument("--bkg-functions", nargs="+", choices=BKG_FUNCTIONS, default=BKG_FUNCTIONS,
                    metavar="FUNC",
                    help=f"candidate background functions (default: all of {', '.join(BKG_FUNCTIONS)})")
    ap.add_argument("--bkg-pvalue-threshold", type=float, default=0.05,
                    help="the best background function must have a p-value above this, "
                         "otherwise the script stops with an error (default: 0.05)")
    ap.add_argument("--sqrts", type=float, default=13600.0,
                    help="centre-of-mass energy in GeV, only used to scale m in the 'dijet' "
                         "functions (default: 13600)")
    args = ap.parse_args()

    degrees = parse_degrees(args.degree, args.default_degree)

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.TH1.AddDirectory(False)
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    line = "=" * 70

    tfile = ROOT.TFile.Open(args.input)
    if not tfile or tfile.IsZombie():
        sys.exit(f"ERROR: cannot open {args.input}")
    hists = load_histograms(tfile, args.hists)
    data_obs = None if args.skip_background else load_data_obs(tfile, args.data_obs)
    tfile.Close()

    # ---- Background first, so that the script fails early if no function describes the data
    background = None
    if data_obs is not None:
        print(f"\n{line}\nBackground fits to '{data_obs.GetName()}'\n{line}")
        data_window = slice_histogram(data_obs, args.xmin_floor, args.xmax)
        background = fit_background_functions(
            data_window, args.bkg_functions, args.errors, args.sqrts,
            args.bkg_pvalue_threshold, outdir, args.formats, hist_name=data_obs.GetName())

    # ---- Step 1: per-mass fits
    fits = {}
    for mass, hist in hists.items():
        print(f"\nFitting '{hist.GetName()}' as m(Z') = {mass} GeV ...")
        fits[mass] = fit_histogram(hist, mass, args.errors, args.xmin_floor, args.xmax)
        make_plot(mass, fits[mass], outdir, args.formats)  # also fills chi2/ndf
        print_fit_result(f"m(Z') = {mass} GeV", fits[mass])

    # ---- Step 2: parameters vs. mass
    masses = sorted(fits)
    if len(masses) < 2:
        sys.exit("ERROR: need at least two mass points to fit parameters vs mass")

    line = "=" * 70
    print(f"\n{line}\nParameter vs. mass fits (polynomials/splines in m = m(Z') in GeV)\n{line}")
    param_fits = {}
    for name in PARAMS:
        vals = [fits[m][name].getVal() for m in masses]
        errs = [fits[m][name].getError() for m in masses]
        param_fits[name] = fit_vs_mass(name, [float(m) for m in masses], vals, errs,
                                       degrees[name], outdir, args.formats,
                                       args.pvalue_threshold)
        pf = param_fits[name]
        if pf["kind"] == "spline":
            print_spline(name, pf)
            continue
        if pf["scan"]:
            print(f"\n  {name}: automatic order selection "
                  f"(accept the lowest order with p-value > {args.pvalue_threshold:g})")
            for t in pf["scan"]:
                print(f"    pol{t['degree']}: chi2/ndf = {t['chi2']:.3f} / {t['ndf']}   "
                      f"p-value = {t['pvalue']:.4f}")
        print(f"\n  {format_polynomial(name, pf['coeffs'])}   [pol{pf['degree']}, {pf['selection']}]")
        for i, (v, e) in enumerate(pf["coeffs"]):
            print(f"    p{i} = {v:.6g} +/- {e:.6g}")
        if pf["ndf"] > 0:
            ptxt = f"   p-value = {pf['pvalue']:.4f}" if pf["pvalue"] is not None else ""
            print(f"    chi2/ndf = {pf['chi2']:.3f} / {pf['ndf']} "
                  f"(= {pf['chi2'] / pf['ndf']:.3f}){ptxt}")
        else:
            print("    ndf = 0 (exact interpolation, no goodness-of-fit)")

    # ---- Step 3: analytic model
    xlo = min(f["xmin"] for f in fits.values())
    xhi = max(f["xmax"] for f in fits.values())
    nbins = max(f["nbins"] for f in fits.values())
    ws_path = outdir / "signal_model.root"
    bkg_best = background["best"] if background else None
    if bkg_best and (abs(bkg_best["xmin"] - xlo) > 1e-6 * (xhi - xlo)
                     or abs(bkg_best["xmax"] - xhi) > 1e-6 * (xhi - xlo)):
        print(f"WARNING: the data_obs window [{bkg_best['xmin']:g}, {bkg_best['xmax']:g}] differs "
              f"from the signal window [{xlo:g}, {xhi:g}] (different binning?); the workspace "
              "observable uses the signal window", file=sys.stderr)
    ws, ws_keep = build_workspace(param_fits, xlo, xhi, masses[0], masses[-1], ws_path,
                                  background=bkg_best, sqrts=args.sqrts)
    val_objs = validation_plot(ws, masses, nbins, outdir, args.formats)

    json_path = outdir / "signal_parametrization.json"
    payload = dict(
        masses=masses,
        mjj_range=[xlo, xhi],
        fit_ranges={str(m): [fits[m]["fit_lo"], fits[m]["fit_hi"]] for m in masses},
        parameters={name: param_to_json(name, pf) for name, pf in param_fits.items()},
    )
    if background:
        payload["background"] = background_to_json(background, args.sqrts,
                                                   args.bkg_pvalue_threshold)
    json_path.write_text(json.dumps(payload, indent=2))

    contents = "w::signal_model (mass variable mZp)"
    if background:
        contents += f", w::bkg_model [{background['best']['func']}]"
    print(f"\n{line}\nSaved:\n  workspace -> {ws_path}  ({contents}; observable mjj)"
          f"\n  JSON      -> {json_path}\n{line}")
    print("Note: the model is only validated within "
          f"[{masses[0]}, {masses[-1]}] GeV; extrapolation is not reliable.")


if __name__ == "__main__":
    main()
