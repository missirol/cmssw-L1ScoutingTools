#!/bin/bash -ex

if [ ! -d ${L1SADIR} ]; then
  exit 1
fi

outtar=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tar) outtar=1; shift;;
    --no-tar) outtar=0; shift;;
  esac
done

inpdir=${L1SADIR}/out2_l1sSelDiJet
outdir=out2_l1sSelDiJet_plots_tmp

rm -rf "${outdir}"{,.tar.gz}

# Data, standard L1T Jets vs L1S Calo Jets
l1sSelDiJet_plots.py \
  -k run3_l1s_dijet01 \
  -m "*Jet*" \
  -i "${inpdir}"/outputs/L1ScoutingSelection_Run2026D.root:'N/A':1:1:20 \
  -o "${outdir}"/L1ScoutingSelection_Run2026D \
  -l "PD: L1ScoutingSelection (Run2026D)" \
  --tr-label "5.6 pb^{-1} (13.6 TeV)" \
  -e pdf

# Data vs Signal MCs
l1sSelDiJet_plots.py \
  -k run3_l1s_dijet02 \
  -m "*Jet*" \
  -i "${inpdir}"/outputs/L1ScoutingSelection_Run2026D.root:'Data':1:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M200_TuneCP5_13p6TeV_pythia8.root:"Z'(200)":632:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M300_TuneCP5_13p6TeV_pythia8.root:"Z'(300)":418:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M400_TuneCP5_13p6TeV_pythia8.root:"Z'(400)":802:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M500_TuneCP5_13p6TeV_pythia8.root:"Z'(500)":882:1:20 \
  -o "${outdir}" \
  -l "" \
  --tr-label "5.6 pb^{-1} (13.6 TeV)" \
  -e pdf

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
