#!/bin/bash -ex

#if [ ! -d ${L1SADIR} ]; then
#  exit 1
#fi

outtar=1
#while [[ $# -gt 0 ]]; do
#  case "$1" in
#    --tar) outtar=1; shift;;
#    --no-tar) outtar=0; shift;;
#  esac
#done

TARGET_DIR=out2_l1sSelDiJet
[ $# -eq 0 ] || TARGET_DIR="${1}"

inpdir=${TARGET_DIR}
outdir=${TARGET_DIR}_plots_tmp

rm -rf "${outdir}"{,.tar.gz}

# L1T Jets vs L1S Calo Jets: Data
l1sSelDiJet_plots.py \
  -k run3_l1s_dijet01 \
  -m "*Jet*" \
  -i "${inpdir}"/outputs/L1ScoutingSelection_Run2026D.root:'N/A':1:1:20 \
  -o "${outdir}"/l1tJetsVsL1SCaloJets_data \
  -l "PD: L1ScoutingSelection (Run2026D)" \
  --tr-label "5.6 pb^{-1} (13.6 TeV)" \
  -e pdf png

# L1T Jets vs L1S Calo Jets: Zp400
l1sSelDiJet_plots.py \
  -k run3_l1s_dijet01 \
  -m "*Jet*" \
  -i "${inpdir}"/outputs/ZprimeToQQ_M400_TuneCP5_13p6TeV_pythia8.root:'N/A':1:2:20 \
  -o "${outdir}"/l1tJetsVsL1SCaloJets_Zp400 \
  -l "Z' #rightarrow q#bar{q}, M(Z')=400 GeV" \
  --tr-label "13.6 TeV" \
  -e pdf png

# Data vs Signal MCs
l1sSelDiJet_plots.py \
  -k run3_l1s_dijet02 \
  -m "*Jet*" \
  -i "${inpdir}"/outputs/L1ScoutingSelection_Run2026D.root:'Data':1:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M200_TuneCP5_13p6TeV_pythia8.root:"Z'(200)":632:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M300_TuneCP5_13p6TeV_pythia8.root:"Z'(300)":418:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M400_TuneCP5_13p6TeV_pythia8.root:"Z'(400)":802:1:20 \
     "${inpdir}"/outputs/ZprimeToQQ_M500_TuneCP5_13p6TeV_pythia8.root:"Z'(500)":882:1:20 \
  -o "${outdir}"/dataVsZPrime \
  -l "" \
  --tr-label "5.6 pb^{-1} (13.6 TeV)" \
  -e pdf png

# Comparing jet-eta cuts on signal samples
for sigmass in 200 300 400 500; do
  l1sSelDiJet_plots.py \
    -k run3_l1s_dijet02 \
    -m "*Jet*" \
    -i "${inpdir}"_eta1p1/outputs/ZprimeToQQ_M"${sigmass}"_TuneCP5_13p6TeV_pythia8.root:"|#eta_{jet}| < 1.1   ":1:1:20 \
       "${inpdir}"_eta2p5/outputs/ZprimeToQQ_M"${sigmass}"_TuneCP5_13p6TeV_pythia8.root:"|#eta_{jet}| < 2.5   ":632:1:20 \
       "${inpdir}"_eta3p0/outputs/ZprimeToQQ_M"${sigmass}"_TuneCP5_13p6TeV_pythia8.root:"|#eta_{jet}| < 3.0   ":418:1:20 \
    -o "${outdir}"/compareJetEtaCut/ZPrimeToQQ_M"${sigmass}" \
    -l "Z' #rightarrow q#bar{q}, M(Z')=${sigmass} GeV" \
    --tr-label "13.6 TeV" \
    -e pdf png
done

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
