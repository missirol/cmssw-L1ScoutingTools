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

# Plots labels of input data sets
declare -A samplesMap
samplesMap["L1ScoutingSelection_Run2026D"]="PD: L1ScoutingSelection (Run2026D)"

for sampleName in ${!samplesMap[@]}; do
  sampleLabel=${samplesMap[${sampleName}]}

  l1sSelDiJet_plots.py \
    -k run3_l1s_dijet01 \
    -m "*Jet*" \
    -i "${inpdir}"/outputs/"${sampleName}".root:'N/A':1:1:20 \
    -o "${outdir}"/"${sampleName}" \
    -l "${sampleLabel}" \
    --tr-label "5.6 pb^{-1}" \
    -e png pdf root
done

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
