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

inpdir=${L1SADIR}/out2_jetResp
outdir=out2_jetResp_plots_tmp

rm -rf "${outdir}"{,.tar.gz}

samples=(
  Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120
)

for sample in "${samples[@]}"; do
  outd_i="${outdir}"/"${sample}"

  ./fitJetResponse.py -k l1s_run3_jecFits \
    -i "${inpdir}"/harvesting/"${sample}".root \
    -o "${outd_i}" \
    -m "*_pt_GENoverREC_Median_wrt_*pt" "*_E_GENoverREC_Median_wrt_*E" \
    -l 'QCD-#hat{p}_{T}[15-7000], PU[0-120] (Run3Winter25)' \
    -e png

done
unset sample outd_i

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
