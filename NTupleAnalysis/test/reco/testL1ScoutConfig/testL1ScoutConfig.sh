#!/bin/bash

[ $# -eq 1 ] || exit 1

JOBLABEL=tmp_l1Scout
#INPUTFILE=/eos/user/m/missirol/l1s_data_250219/run000001/run000001_ls0770_index000063.raw
#RUNNUMBER=000001
#INPUTFILE=/eos/user/m/missirol/l1s_data_250306/run398183/run398183_ls0261_index000000.raw
#RUNNUMBER=398183
INPUTFILE=/eos/user/m/missirol/l1s_data_250401/run402562/run402562_ls6099_index000050.raw
RUNNUMBER=402562
MAXORBITS=-1

wget "${1}" -O "${JOBLABEL}"_cfg.py

sed -i "s|(!%BU_BASE_DIRS_ALL%!)||g" "${JOBLABEL}"_cfg.py
sed -i "s|(!%BU_BASE_DIRS_NUM_STREAMS%!)||g" "${JOBLABEL}"_cfg.py
sed -i "s|(!%FILE_BROKER_HOST%!)|''|g" "${JOBLABEL}"_cfg.py
sed -i "s|(!%PRESCALE%!)|1|g" "${JOBLABEL}"_cfg.py

cat <<@EOF >> "${JOBLABEL}"_cfg.py
process.source.fileListMode = True
process.source.fileNames = ['${INPUTFILE}']

process.EvFDaqDirector.runNumber = ${RUNNUMBER}
process.EvFDaqDirector.baseDir = '.'
process.EvFDaqDirector.buBaseDir = './tmp'
process.EvFDaqDirector.buBaseDirsAll = [process.EvFDaqDirector.buBaseDir.value()]
process.EvFDaqDirector.buBaseDirsNumStreams = [1]
process.EvFDaqDirector.useFileBroker = False

process.options.numberOfThreads = 1
process.options.numberOfStreams = 0

process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.maxEvents.input = ${MAXORBITS}

for outModLabel in process.outputModules_():
    outMod = getattr(process, outModLabel)
    setattr(process, outModLabel, cms.OutputModule("PoolOutputModule",
        **outMod.parameters_(),
        fileName = cms.untracked.string( f"${JOBLABEL}_output_{outModLabel}.root" )
    ))
    outMod = getattr(process, outModLabel)
    del outMod.SelectEvents

del process.epL1ScoutingSelection
del process.scPrescaler
@EOF

rm -rf tmp run"${RUNNUMBER}"

cmsRun "${JOBLABEL}"_cfg.py 2>&1 | tee "${JOBLABEL}"_cfg.log

rm -rf tmp run"${RUNNUMBER}"
