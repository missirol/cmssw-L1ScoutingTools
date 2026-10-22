#!/usr/bin/env python3
"""
Plot expected 95% CL upper limits (median, "Expected 50.0%") as a function
of signal mass for an arbitrary number of analysis categories, using PyROOT.

The input is the plain-text log produced by running `combine` on a set of
datacards. Each result block starts with a header line

    datacard_[CATEGORY]_ZPqq[MASS].txt

and contains a line

    Expected 50.0%: r < [NUMBER]

Everything else (e.g. the leading list of 'datacard_*.root' files, other
quantiles, banner lines) is ignored.

Examples
--------
  # see what the file contains
  python plot_limits.py limits.txt --list-categories

  # plot two categories
  python plot_limits.py limits.txt \\
      -c L005p6pb_L1TJet_Std_Mjj150 L005p6pb_L1SCaloJet_Std_Mjj150 \\
      --colors 1 2 \\
      --legend-labels 'L1 TJet' 'L1 SCaloJet' \\
      --top-left '#bf{CMS} #it{Preliminary}' --top-right '5.6 pb^{-1} (13.6 TeV)' \\
      --text '|#eta| < 3.0' --logy -o limits_plot

Notes
-----
* Put the input file right after the script name: options such as
  --categories take a variable number of values.
* Texts containing '#' (TLatex) must be quoted in the shell.
* --colors takes ROOT colour indices (e.g. 1=kBlack, 2=kRed, 4=kBlue,
  632=kRed, 600=kBlue, 416=kGreen).
"""

import argparse
import difflib
import os
import re
import sys

# Default colour-blind friendly palette (Petroff 10-colour scheme), used when
# --colors is not given.
PALETTE_HEX = [
    "#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6",
    "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd",
]
MARKERS = [20, 21, 22, 23, 33, 34, 29, 47, 43, 45]

# "datacard_[CATEGORY]_ZPqq[MASS].txt"  (the "...root" lines of the initial
# file listing do not match because of the ".txt" suffix)
HEADER_RE = re.compile(r"^datacard_(?P<category>.+)_ZPqq(?P<mass>\d+)\.txt\s*$")
# "Expected 50.0%: r < [NUMBER]"
EXP50_RE = re.compile(r"^Expected\s+50\.0%\s*:\s*r\s*<\s*(?P<value>[-+0-9.eE]+)\s*$")


def warn(msg):
    print("WARNING: %s" % msg, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_limits(path):
    """
    Parse the text file and return a dictionary

        { CATEGORY : [ (MASS, NUMBER), ... ] }

    with the list sorted by mass. MASS is an int, NUMBER is the float found in
    the "Expected 50.0%: r < NUMBER" line of the corresponding block.
    """
    collected = {}   # category -> {mass: value}
    current = None   # (category, mass, line number) of the block being read

    with open(path) as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()

            m = HEADER_RE.match(line)
            if m:
                if current is not None:
                    warn("no 'Expected 50.0%%' line found for block '%s' mass %d (line %d)"
                         % (current[0], current[1], current[2]))
                current = (m.group("category"), int(m.group("mass")), lineno)
                continue

            m = EXP50_RE.match(line)
            if m:
                if current is None:
                    warn("line %d: 'Expected 50.0%%' found outside of a datacard block, ignored" % lineno)
                    continue
                category, mass, _ = current
                try:
                    value = float(m.group("value"))
                except ValueError:
                    warn("line %d: cannot convert '%s' to a number" % (lineno, m.group("value")))
                    continue
                entries = collected.setdefault(category, {})
                if mass in entries:
                    warn("duplicate entry for category '%s', mass %d (line %d): keeping the last one"
                         % (category, mass, lineno))
                entries[mass] = value
                current = None   # block done

    if current is not None:
        warn("no 'Expected 50.0%%' line found for block '%s' mass %d (line %d)"
             % (current[0], current[1], current[2]))

    return {cat: sorted(entries.items()) for cat, entries in collected.items()}


# --------------------------------------------------------------------------- #
# Command line
# --------------------------------------------------------------------------- #
def parse_args():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    p.add_argument("input", help="text file with the limits (combine output)")
    p.add_argument("--list-categories", action="store_true",
                   help="print the categories (and masses) found in the input file and exit")

    sel = p.add_argument_group("what to plot")
    sel.add_argument("-c", "--categories", nargs="+", metavar="CATEGORY",
                     help="categories to plot (exact names, as in datacard_[CATEGORY]_ZPqq[MASS].txt)")
    sel.add_argument("--colors", nargs="+", type=int, metavar="COLOR",
                     help="ROOT colour index for each category, in the same order as --categories "
                          "(default: built-in palette)")
    sel.add_argument("--scale", type=float, default=1.0,
                     help="multiply all numbers by this factor, e.g. the reference cross section "
                          "that the signal was normalised to (default: 1)")

    lab = p.add_argument_group("labels (TLatex syntax; quote them in the shell)")
    lab.add_argument("--legend-labels", nargs="+", metavar="LABEL",
                     help="legend text for each category, same order as --categories "
                          "(default: the category names)")
    lab.add_argument("--legend-header", help="title of the legend")
    lab.add_argument("--top-left", default="", help="text above the frame, left-aligned")
    lab.add_argument("--top-right", default="", help="text above the frame, right-aligned")
    lab.add_argument("--text", action="append", default=[], metavar="LINE",
                     help="text inside the frame, top-left; repeat the option for several lines")
    lab.add_argument("--xtitle", default="m_{Z'} [GeV]", help="x-axis title")
    lab.add_argument("--ytitle", default="Expected 95% CL upper limit on #sigma #times BR [nb]",
                     help="y-axis title")

    sty = p.add_argument_group("style and output")
    sty.add_argument("--logy", action="store_true", help="logarithmic y axis")
    sty.add_argument("--logx", action="store_true", help="logarithmic x axis")
    sty.add_argument("--grid", action="store_true", help="draw grid")
    sty.add_argument("--no-markers", action="store_true", help="lines only, no markers")
    sty.add_argument("--xrange", nargs=2, type=float, metavar=("XMIN", "XMAX"))
    sty.add_argument("--yrange", nargs=2, type=float, metavar=("YMIN", "YMAX"))
    sty.add_argument("--legend-pos", nargs=4, type=float, metavar=("X1", "Y1", "X2", "Y2"),
                     help="legend corners in NDC (default: top-right)")
    sty.add_argument("--legend-ncols", type=int, default=1, help="number of legend columns")
    sty.add_argument("-o", "--output", default="limits",
                     help="output basename, without extension (default: limits)")
    sty.add_argument("--formats", nargs="+", default=["pdf", "png"],
                     help="output formats (default: pdf png)")
    return p.parse_args()


def select_categories(limits, args):
    """Return [(category, [(mass, value), ...]), ...] for the requested categories."""
    missing = [c for c in args.categories if c not in limits]
    if missing:
        lines = []
        for c in missing:
            close = difflib.get_close_matches(c, list(limits), n=3, cutoff=0.6)
            hint = " (did you mean: %s ?)" % ", ".join(close) if close else ""
            lines.append("  '%s'%s" % (c, hint))
        sys.exit("Error: categories not found in '%s':\n%s\nUse --list-categories to see what is available."
                 % (args.input, "\n".join(lines)))

    n = len(args.categories)
    if args.colors is not None and len(args.colors) != n:
        sys.exit("Error: got %d colours for %d categories" % (len(args.colors), n))
    if args.legend_labels is not None and len(args.legend_labels) != n:
        sys.exit("Error: got %d legend labels for %d categories" % (len(args.legend_labels), n))

    return [(c, limits[c]) for c in args.categories]


# --------------------------------------------------------------------------- #
# Plotting
# --------------------------------------------------------------------------- #
def make_plot(selected, args):
    import ROOT   # imported here so that parsing / --list-categories work without ROOT

    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)

    keep = []   # Python references, so that ROOT objects are not garbage-collected

    # ---- colours / labels
    if args.colors is not None:
        colors = list(args.colors)
    else:
        colors = [ROOT.TColor.GetColor(h) for h in PALETTE_HEX]
    labels = args.legend_labels if args.legend_labels is not None else [c for c, _ in selected]

    # ---- canvas
    canv = ROOT.TCanvas("c", "c", 800, 700)
    canv.SetLeftMargin(0.14)
    canv.SetRightMargin(0.05)
    canv.SetTopMargin(0.07)
    canv.SetBottomMargin(0.12)
    canv.SetTicks(1, 1)
    if args.logy:
        canv.SetLogy()
    if args.logx:
        canv.SetLogx()
    if args.grid:
        canv.SetGrid()

    # ---- data, with the optional overall scale applied
    data = [(cat, [(m, v * args.scale) for m, v in pts]) for cat, pts in selected]
    all_m = [m for _, pts in data for m, _ in pts]
    all_v = [v for _, pts in data for _, v in pts]

    # ---- axis ranges
    if args.xrange:
        xmin, xmax = args.xrange
    else:
        pad = 0.05 * (max(all_m) - min(all_m)) if max(all_m) > min(all_m) else 10.0
        xmin, xmax = min(all_m) - pad, max(all_m) + pad

    if args.yrange:
        ymin, ymax = args.yrange
    elif args.logy:
        pos = [v for v in all_v if v > 0]
        ymin, ymax = min(pos) / 3.0, max(pos) * 30.0      # headroom for the legend
    else:
        span = max(all_v) - min(all_v)
        ymin, ymax = max(0.0, min(all_v) - 0.05 * span), max(all_v) + 0.45 * span

    frame = ROOT.TH1F("frame", "", 100, xmin, xmax)
    frame.SetMinimum(ymin)
    frame.SetMaximum(ymax)
    xax, yax = frame.GetXaxis(), frame.GetYaxis()
    xax.SetTitle(args.xtitle)
    yax.SetTitle(args.ytitle)
    for ax in (xax, yax):
        ax.SetTitleSize(0.045)
        ax.SetLabelSize(0.04)
        ax.SetTitleFont(42)
        ax.SetLabelFont(42)
    xax.SetTitleOffset(1.1)
    yax.SetTitleOffset(1.4)
    frame.Draw("AXIS")
    keep.append(frame)

    # ---- legend
    if args.legend_pos:
        x1, y1, x2, y2 = args.legend_pos
    else:
        rows = (len(data) + args.legend_ncols - 1) // args.legend_ncols
        rows += 1 if args.legend_header else 0
        x1, x2, y2 = 0.50, 0.93, 0.89
        y1 = y2 - min(0.05 * rows, 0.50)
    leg = ROOT.TLegend(x1, y1, x2, y2)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.034)
    leg.SetNColumns(args.legend_ncols)
    if args.legend_header:
        leg.SetHeader(args.legend_header)
    keep.append(leg)

    # ---- curves
    for i, (cat, pts) in enumerate(data):
        col = colors[i % len(colors)]
        g = ROOT.TGraph(len(pts))
        for j, (m, v) in enumerate(pts):
            g.SetPoint(j, m, v)
        g.SetName("limit_%s" % cat)
        g.SetLineColor(col)
        g.SetLineWidth(3)
        g.SetMarkerColor(col)
        g.SetMarkerStyle(MARKERS[i % len(MARKERS)])
        g.SetMarkerSize(1.1)
        g.Draw("L same" if args.no_markers else "LP same")
        leg.AddEntry(g, labels[i], "L" if args.no_markers else "LP")
        keep.append(g)
    leg.Draw()

    # ---- labels
    lat = ROOT.TLatex()
    lat.SetNDC()
    lat.SetTextFont(42)

    if args.top_left:
        lat.SetTextAlign(11)
        lat.SetTextSize(0.040)
        lat.DrawLatex(0.14, 0.945, args.top_left)
    if args.top_right:
        lat.SetTextAlign(31)
        lat.SetTextSize(0.038)
        lat.DrawLatex(0.95, 0.945, args.top_right)

    lat.SetTextAlign(13)
    lat.SetTextSize(0.036)
    for k, line in enumerate(args.text):
        lat.DrawLatex(0.17, 0.89 - 0.05 * k, line)

    ROOT.gPad.RedrawAxis()
    canv.Update()

    # ---- save
    outdir = os.path.dirname(args.output)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    for fmt in args.formats:
        fname = "%s.%s" % (args.output, fmt)
        canv.SaveAs(fname)


# --------------------------------------------------------------------------- #
def main():
    args = parse_args()

    try:
        limits = parse_limits(args.input)
    except OSError as exc:
        sys.exit("Error reading '%s': %s" % (args.input, exc))
    if not limits:
        sys.exit("Error: no 'datacard_[CATEGORY]_ZPqq[MASS].txt' blocks with an "
                 "'Expected 50.0%%' line found in '%s'" % args.input)

    if args.list_categories:
        for cat in sorted(limits):
            print("%s   masses: %s" % (cat, ", ".join(str(m) for m, _ in limits[cat])))
        return

    if not args.categories:
        sys.exit("Error: no categories given; use --categories (or --list-categories)")

    selected = select_categories(limits, args)
    make_plot(selected, args)


if __name__ == "__main__":
    main()
