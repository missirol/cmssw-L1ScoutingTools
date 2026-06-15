#!/bin/bash

shopt -s expand_aliases
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env

BRIL_NORMTAG=/cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json

brilcalc_cmd(){
  brilcalc lumi -u /fb -c web -b "STABLE BEAMS" --without-checkjson \
   --normtag "${BRIL_NORMTAG}" --hltpath HLT_ZeroBias_v* $@
}

#brilcalc_cmd -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json
#brilcalc_cmd -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json
#brilcalc_cmd -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json
#brilcalc_cmd -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions25/Cert_Collisions2025_391658_398903_Golden.json
#brilcalc_cmd -i /eos/user/c/cmsdqm/www/CAF/certification/Collisions26/Collisions26_MLEnhancedGolden_Latest.json

python3 -c """
import json
ret = dict()
for input_json in [
    '/eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json',
    '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json',
    '/eos/user/c/cmsdqm/www/CAF/certification/Collisions24/Cert_Collisions2024_378981_386951_Golden.json',
    '/eos/user/c/cmsdqm/www/CAF/certification/Collisions25/Cert_Collisions2025_391658_398903_Golden.json',
    '/eos/user/c/cmsdqm/www/CAF/certification/Collisions26/Collisions26_MLEnhancedGolden_Latest.json',
]:
    ret.update(json.load(open(input_json)))
json.dump(ret, open('tmp.json', 'w'), sort_keys=True, indent=4)
"""
brilcalc_cmd -i tmp.json
rm -f tmp.json
