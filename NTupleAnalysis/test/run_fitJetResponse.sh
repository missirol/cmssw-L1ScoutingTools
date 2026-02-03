#!/bin/bash

INPDIR=out2_jetResp
OUTDIR=out2_jetResp_plots_tmp

rm -rf "${OUTDIR}"

./fitJetResponse.py -k l1s_run3_jecFits \
  -i "${INPDIR}"/harvesting/*root \
  -o "${OUTDIR}" \
  -m "*_pt_GENoverREC_Median_wrt_*pt" \
  -l 'QCD-#hat{p}_{T}[15-7000], PU[0-120] (Run3Winter25)' \
  -e png
