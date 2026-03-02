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

samples=(
  Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120
)

for sample in "${samples[@]}"; do
  outd_i="${outdir}"/"${sample}"

  opts_i=""
  if [[ ${sample} == *"QCD_"* ]]; then
    opts_i="-m '*Jet*'"
  fi

  jetMETPerformance_plots.py \
    -k run3_l1s_jetperf \
    ${opts_i} \
    -i ${inpdir}/harvesting/${sample}.root:'N/A':1:1:20 \
    -o ${outd_i} \
    -l ${sample} \
    -e png pdf
done

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
