#!/bin/bash

rm -f json1819_pp2026_certCaloOnly.json
wget https://cernbox.cern.ch/remote.php/dav/public-files/Dxdcs0XwLwuH5z8/\
json1819_pp2026_certCaloOnly.json

shopt -s expand_aliases
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env

BRIL_NORMTAG=/cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json

brilcalc_cmd(){
  brilcalc lumi $@ -u /fb -c web -b "STABLE BEAMS" --without-checkjson \
   --normtag "${BRIL_NORMTAG}"
}

# Run2026B (delivered and recorded)
brilcalc_cmd --begin 401837 --end 402513
# Run2026B (calo-only certified)
brilcalc_cmd --begin 401837 --end 402513 -i json1819_pp2026_certCaloOnly.json

# Run2026D (delivered and recorded)
brilcalc_cmd --begin 403423 --end 404067
# Run2026D (calo-only certified)
brilcalc_cmd --begin 403423 --end 404067 -i json1819_pp2026_certCaloOnly.json

# Run2026B+Run2026D (usable for physics analysis with L1S CaloTowers)
l1sCaloTowersJson2026 -i json1819_pp2026_certCaloOnly.json -v \
 --normtag "${BRIL_NORMTAG}"

# Temp file
cat <<@EOF > tmp_lumi.json
{
  "402512": [[300, 300]],
  "403441": [[100, 100]],
  "403937": [[501, 550]]
}
@EOF

brilcalc_cmd --begin 403423 --end 404067 -i tmp_lumi.json
