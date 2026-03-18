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

inpdir=${L1SADIR}/out2_jetPerf
outdir=out2_jetPerf_plots_tmp

rm -rf "${outdir}"{,.tar.gz}

# Plots labels of input data sets
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_EpsilonPU"]="QCD-#hat{p}_{T}[15-7000], EpsilonPU (Run3Winter25)"
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120"]="QCD-#hat{p}_{T}[15-7000], PU[0-120] (Run3Winter25)"
samplesMap["Run3Winter25_TTbar_13p6TeV"]="TTbar (Run3Winter25)"

for sampleName in ${!samplesMap[@]}; do
  sampleLabel=${samplesMap[${sampleName}]}

  jetMETPerformance_plots.py \
    -k run3_l1s_jetperf \
    -m "*Jet*" \
    -i "${inpdir}"/harvesting/"${sampleName}".root:'N/A':1:1:20 \
    -o "${outdir}"/"${sampleName}" \
    -l "${sampleLabel}" \
    -e png pdf
done

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
