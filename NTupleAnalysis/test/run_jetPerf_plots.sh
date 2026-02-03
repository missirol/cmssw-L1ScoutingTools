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
outdir=plots_jetPerf

samples=(
  Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120
)

if [ ${outtar} -gt 0 ] && [ -f ${outdir}.tar.gz ]; then
  printf "%s\n" ">> target output file already exists: ${outdir}.tar.gz"
  exit 1
fi

if [ -d ${outdir} ]; then
  printf "%s\n" ">> target output directory already exists: \"${outdir}\""
  exit 1
fi

for sample in "${samples[@]}"; do
  outd_i=${outdir}/${sample}

  opts_i=""
  if [[ ${sample} == *"QCD_"* ]]; then opts_i="-m '*Jet*' -s '*MET_*' '*/offline*MET*_pt' '*MET*GEN*'" #!!
#!!  if [[ ${sample} == *"QCD_"* ]]; then opts_i="-m '*Jet*HB*' -s '*MET_*' '*/offline*MET*_pt' '*MET*GEN*'" #!!
  fi

  jetMETPerformance_plots.py -k run3_l1s_jetperf ${opts_i} \
    -o ${outd_i}/run3_l1s_jetperf -l ${sample} -e png pdf -i \
    ${inpdir}/harvesting/${sample}.root:'N/A':1:1:20
done

if [ ${outtar} -gt 0 ] && [ -d ${outdir} ]; then
  tar cfz ${outdir}.tar.gz ${outdir}
  rm -rf ${outdir}
fi
