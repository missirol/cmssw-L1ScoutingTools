#!/bin/bash -e

JOBLABEL=tmp_l1Scout
INPUTFILE=/store/data/Run2026D/L1Scouting/L1SCOUT/v1/000/403/937/00000/6dfcc5f7-8d37-44f3-80ea-fec41eb1e76f.root
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

from L1TriggerScouting.OnlineProcessing.L1ScoutingCaloJetOrbitProducer import L1ScoutingCaloJetOrbitProducer
process.l1ScCaloJets = L1ScoutingCaloJetOrbitProducer(
    src = 'l1ScCaloTowerUnpacker:CaloTower',
    akR = 0.4,
    towerMinHwEt = 1,
    towerMaxHwEt = -1,
    ptMin = 5,
    applyJECs = True,
    jecFile = 'L1TriggerScouting/OnlineProcessing/data/JEC_AK4CaloTowerL1S_Run3Winter25_v2.txt',
    jecPUProxyTowerMinHwEt = 1,
    jecPUProxyTowerMaxHwEt = -1,
    jecPUProxyTowerMinAbsHwEta = 0,
    jecPUProxyTowerMaxAbsHwEta = 4,
    produceSortedCaloTowers = True,
    mantissaPrecision = 10
)

from L1TriggerScouting.OnlineProcessing.CaloJetBxSelector import CaloJetBxSelector
process.CaloDijet30 = CaloJetBxSelector(
    jetsTag = 'l1ScCaloJets:CaloJet',
    minNJet = 2,
    minJetPt = [40, 30],
    maxJetAbsEta = [2.5, -1],
    minJetNConst = [0, 0],
)

from L1TriggerScouting.OnlineProcessing.MaskOrbitBxScoutingCaloJet import MaskOrbitBxScoutingCaloJet
process.BxSelectorCaloJet = MaskOrbitBxScoutingCaloJet(
    dataTag = 'l1ScCaloJets:CaloJet',
    selectBxs = 'CaloDijet30:SelBx',
    productLabel = 'CaloJet',
)

process.L1ScoutingPath = cms.Path(
    process.l1ScCaloJets
  + process.CaloDijet30
  + process.BxSelectorCaloJet
)

from IOPool.Output.PoolOutputModule import PoolOutputModule
process.l1sOutputModule = PoolOutputModule(
    fileName = '${JOBLABEL}_step1_out.root',
    outputCommands = [
        'keep *',
        'drop edmTriggerResults_*_*_*',
        'drop *_l1ScCaloTowerUnpacker_*_*',
        'keep *_l1ScCaloJets_*_*',
        'keep *_CaloDijet30_*_*',
        'keep *_BxSelectorCaloJet_*_*',
    ]
)

process.L1ScoutingOutputEndPath = cms.EndPath(process.l1sOutputModule)

process.MessageLogger.cerr.threshold = 'DEBUG'
process.MessageLogger.debugModules = ['l1ScCaloJets']
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

process.l1scoutingCaloJetTable = cms.EDProducer("SimpleL1ScoutingCaloJetOrbitFlatTableProducer",
    src = cms.InputTag("l1ScCaloJets:CaloJet"),
    name = cms.string("L1CaloJet"),
    doc = cms.string("AK4 Jets based on CaloTowers from Calo Layer-1"),
    singleton = cms.bool(False),
    skipNonExistingSrc = cms.bool(False),
    variables = cms.PSet(
        pt = Var("pt()", "float", doc="jet pT", precision=10),
        eta = Var("eta()", "float", doc="jet eta", precision=10),
        phi = Var("phi()", "float", doc="jet phi", precision=10),
        mass = Var("mass()", "float", doc="jet mass", precision=10),
        energyCorr = Var("energyCorr()", "float", doc="correction factor applied to the jet-energy scale"),
        energyFracEm = Var("energyFracEm()", "float", doc="EM fraction of the jet's total energy"),
        nConst = Var("nConst()", "int", doc="number of jet constituents"),
        nConstSaturatedEnergyECAL = Var("nConstSaturatedEnergyECAL()", "uint16", doc="number of jet constituents with saturated ECAL energy"),
        nConstSaturatedEnergyHCAL = Var("nConstSaturatedEnergyHCAL()", "uint16", doc="number of jet constituents with saturated HCAL energy"),
        nConstSaturatedEnergyECALAndHCAL = Var("nConstSaturatedEnergyECALAndHCAL()", "uint16", doc="number of jet constituents with saturated energy in both ECAL and HCAL"),
    )
)

process.l1scoutingCaloTowerPhysicalValueMap.src = 'l1ScCaloJets:SortedCaloTowers'
process.l1scoutingCaloTowerTable.src = 'l1ScCaloJets:SortedCaloTowers'

process.l1scoutingNanoTask.add(process.l1scoutingCaloJetTable)
@EOF

edmConfigDump "${JOBLABEL}"_step2_cfg.py > "${JOBLABEL}"_step2_cfg_dump.py

cmsRun "${JOBLABEL}"_step2_cfg_dump.py 2>&1 | tee "${JOBLABEL}"_step2_cfg_dump.log

rm -rf __pycache__
