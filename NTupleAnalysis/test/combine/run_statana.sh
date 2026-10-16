#!/bin/bash

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

"${THIS_DIR}"/datacards_maker.py \
  -i "${THIS_DIR}"/../out2_l1sSelDiJet/outputs/*.root \
  --lumi 5.6 \
  --fake-bkg

for txtFile in $(ls *L1*Std*400*txt | sort -u); do
  echo "======================================"
  echo ${txtFile}
  echo "======================================"
  combine "${txtFile}" -M AsymptoticLimits --run blind
done
