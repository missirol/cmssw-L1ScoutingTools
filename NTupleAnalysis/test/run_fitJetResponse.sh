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

declare -A samplesMap

# QCD Pt-Flat
#samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_EpsilonPU"]="QCD-#hat{p}_{T}[15-7000], EpsilonPU (Run3Winter25)"
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120"]="QCD-#hat{p}_{T}[15-7000], PU[0-120] (Run3Winter25)"

for sampleName in ${!samplesMap[@]}; do
  sampleLabel=${samplesMap[${sampleName}]}

  common_opts="-i ${inpdir}/harvesting/${sampleName}.root"

  common_opts+=" -e png pdf"

  # Fit Method #1 (JEC as function of Reco-pT)
  ./fitJetResponse.py ${common_opts} -k l1s_run3_jecFitsMethod1 \
    -o ${outdir}/${sampleName}/l1s_run3_jecFitsMethod1 \
    -l "${sampleLabel}" -m "*_pt_GENoverREC_Median_wrt_*pt"

  # Fit Method #2 (GEN-pT as function of Reco-pT)
  ./fitJetResponse.py ${common_opts} -k l1s_run3_jecFitsMethod2 \
    -o ${outdir}/${sampleName}/l1s_run3_jecFitsMethod2 \
    -l "${sampleLabel}" -m "*_pt__vs__GEN_pt"

#  # Closure Plots (profile of GEN/Reco median vs GEN-pT)
#  ./fitJetResponse.py ${common_opts} -k l1s_run3_jecClosurePlots \
#    -o ${outdir}/${sampleName}/l1s_run3_jecClosurePlots \
#    -m "*_pt_overGEN_*Median_wrt_*pt"
done

if [ ${outtar} -gt 0 ] && [ -d "${outdir}" ]; then
  tar cfz "${outdir}".tar.gz "${outdir}"
  rm -rf "${outdir}"
fi
