#!/bin/bash -e

# cmsswRelease=CMSSW_16_0_6_patch1
# cmsswBranch=missirol:devel_l1sCaloJECs_160X
#
# cmsrel "${cmsswRelease}"
# cd "${cmsswRelease}"/src
# cmsenv
# git cms-init --ssh
# git cms-merge-topic "${cmsswBranch}"
#
# git clone https://github.com/missirol/L1TriggerScouting-OnlineProcessing.git \
#  L1TriggerScouting/OnlineProcessing/data
#
# scram b

JOBLABEL=tmp_l1Scout
INPUTFILE=file:/eos/cms/tier0/store/data/Run2026C/L1Scouting/L1SCOUT/v1/000/403/166/00000/7691926b-b588-4e29-9887-fa76f0294480.root
MAXORBITS=10

###
### Step-1 (Add CaloJets, on top of L1SCOUT)
###
cat <<@EOF > "${JOBLABEL}"_step1_cfg.py
import FWCore.ParameterSet.Config as cms

process = cms.Process('TEST')

process.maxEvents.input = ${MAXORBITS}

process.options.numberOfThreads = 1
process.options.numberOfStreams = 0

process.MessageLogger.cerr.FwkReport.reportEvery = 1

from IOPool.Input.PoolSource import PoolSource
process.source = PoolSource(fileNames = ['${INPUTFILE}'])

from L1TriggerScouting.OnlineProcessing.L1ScoutingCaloJetProducer import L1ScoutingCaloJetProducer
process.l1ScAK4CaloTowerJets = L1ScoutingCaloJetProducer(
    src = 'l1ScCaloTowerUnpacker:CaloTower',
    akR = 0.4,
    ptMin = 5,
    towerMinHwEt = 1,
    towerMaxHwEt = -1,
    applyJECs = True,
    jecFile = 'L1TriggerScouting/OnlineProcessing/data/JEC_AK4CaloTowerL1S_Run3Winter25_v2.txt',
    jecPUProxyTowerMinHwEt = 1,
    jecPUProxyTowerMaxHwEt = -1,
    jecPUProxyTowerMinAbsHwEta = 0,
    jecPUProxyTowerMaxAbsHwEta = 4,
    mantissaPrecision = 10
)

from L1TriggerScouting.OnlineProcessing.CaloJetBxSelector import CaloJetBxSelector
process.CaloDijet30 = CaloJetBxSelector(
    jetsTag = 'l1ScAK4CaloTowerJets:CaloJet',
    minNJet = 2,
    minJetPt = [40, 30],
    maxJetAbsEta = [2.5, -1],
    minJetNConst = [0, 0],
)

from L1TriggerScouting.OnlineProcessing.MaskOrbitBxScoutingCaloJet import MaskOrbitBxScoutingCaloJet
process.BxSelectorCaloJet = MaskOrbitBxScoutingCaloJet(
    dataTag = 'l1ScAK4CaloTowerJets:CaloJet',
    selectBxs = 'CaloDijet30:SelBx',
    productLabel = 'CaloJet',
)

process.L1ScoutingPath = cms.Path(
    process.l1ScAK4CaloTowerJets
  + process.CaloDijet30
  + process.BxSelectorCaloJet
)

from IOPool.Output.PoolOutputModule import PoolOutputModule
process.l1sOutputModule = PoolOutputModule(
    fileName = '${JOBLABEL}_step1_out.root',
    outputCommands = [
        'keep *',
        'drop edmTriggerResults_*_*_*',
        'keep *_l1ScAK4CaloTowerJets_*_*',
        'keep *_CaloDijet30_*_*',
        'keep *_BxSelectorCaloJet_*_*',
    ]
)

process.L1ScoutingOutputEndPath = cms.EndPath(process.l1sOutputModule)

process.MessageLogger.cerr.threshold = 'DEBUG'
process.MessageLogger.debugModules = ['l1ScAK4CaloTowerJets']
@EOF

edmConfigDump "${JOBLABEL}"_step1_cfg.py > "${JOBLABEL}"_step1_cfg_dump.py 

cmsRun "${JOBLABEL}"_step1_cfg_dump.py 2>&1 | tee "${JOBLABEL}"_step1_cfg_dump.log

###
### Step-2 (NanoAOD)
###
cmsDriver.py step2 -s NANO:@L1Scout -n -1 --no_exec \
  --process NANO --eventcontent NANOAOD --datatier NANOAOD \
  --data --conditions auto:run3_data_prompt \
  --era Run3_2026 \
  --filein file:"${JOBLABEL}"_step1_out.root \
  --fileout "${JOBLABEL}"_step2_out.root \
  --python_filename "${JOBLABEL}"_step2_cfg.py

cat <<@EOF >> "${JOBLABEL}"_step2_cfg.py

from PhysicsTools.NanoAOD.common_cff import Var

process.l1scoutingAK4CaloJetsTable = cms.EDProducer("SimpleL1ScoutingCaloJetOrbitFlatTableProducer",
    src = cms.InputTag("l1ScAK4CaloTowerJets:CaloJet"),
    name = cms.string("L1CaloJet"),
    doc = cms.string("AK4 CaloTowerJets"),
    singleton = cms.bool(False),
    skipNonExistingSrc = cms.bool(False),
    variables = cms.PSet(
        pt = Var("pt()", "float", doc="pt", precision=10),
        eta = Var("eta()", "float", doc="eta", precision=10),
        phi = Var("phi()", "float", doc="phi", precision=10),
        mass = Var("mass()", "float", doc="mass", precision=10),
        energyCorr = Var("energyCorr()", "float", doc="Energy-scale correction applied to the jet", precision=10),
        nConst = Var("nConst()", "int", doc="Number of jet constituents (CaloTowers)"),
    )
)

process.l1scoutingNanoTask.add(process.l1scoutingAK4CaloJetsTable)
@EOF

edmConfigDump "${JOBLABEL}"_step2_cfg.py > "${JOBLABEL}"_step2_cfg_dump.py

cmsRun "${JOBLABEL}"_step2_cfg_dump.py 2>&1 | tee "${JOBLABEL}"_step2_cfg_dump.log

rm -rf __pycache__
