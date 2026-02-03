import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.l1trig_cff import *

##
## NanoAOD tables for emulated L1T CaloTowers and CaloClusters
##
l1EmulCaloTowerTable = cms.EDProducer("SimpleTriggerL1CaloTowerFlatTableProducer",
    src = cms.InputTag("simCaloStage2Layer1Digis"),
    name = cms.string("L1EmulCaloTower"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string("hwPt > 0"),
    doc = cms.string(""),
    extension = cms.bool(False),
    variables = cms.PSet(
        iet = Var("hwPt()", "int", doc=""),
        ieta = Var("hwEta()", "int", doc=""),
        iphi = Var("hwPhi()", "int", doc=""),
        iem = Var("hwEtEm()", "int", doc=""),
        ihad = Var("hwEtHad()", "int", doc=""),
        iratio = Var("hwEtRatio()", "int", doc=""),
        iqual = Var("hwQual()", "int", doc="")
    )
)

l1EmulCaloClusterTable = cms.EDProducer("SimpleTriggerL1CaloClusterFlatTableProducer",
    src = cms.InputTag("simCaloStage2Digis", "MP"),
    name = cms.string("L1EmulCaloCluster"),
    minBX = cms.int32(0),
    maxBX = cms.int32(0),
    cut = cms.string("hwPt > 0"),
    doc = cms.string(""),
    extension = cms.bool(False),
    variables = cms.PSet(
        iet = Var("hwPt()", "int", doc=""),
        ieta = Var("hwEta()", "int", doc=""),
        iphi = Var("hwPhi()", "int", doc=""),
        iqual = Var("hwQual()", "int", doc=""),
        ietEm = Var("hwPtEm()", "int", doc=""),
        ietHad = Var("hwPtHad()", "int", doc=""),
        ietSeed = Var("hwSeedPt()", "int", doc=""),
        ietaFG = Var("fgEta()", "int", doc=""),
        iphiFG = Var("fgPhi()", "int", doc=""),
        iHoE = Var("hOverE()", "int", doc=""),
        iEcalFG = Var("fgECAL()", "int", doc=""),
        iClusterFlags = Var("clusterFlags()", "int", doc=""),
    )
)

##
## NanoAOD tables for emulated L1T muons, e/gammas, taus, jets and Et-sums
## (customised clones of the modules used in central NANOAOD for unpacked L1T objects)
##
l1EmulMuTable = l1MuTable.clone(
    src = "simGmtStage2Digis",
    name = "L1EmulMu",
)

l1EmulEGTable = l1EGTable.clone(
    src = "simCaloStage2Digis",
    name = "L1EmulEG",
)

l1EmulTauTable = l1TauTable.clone(
    src = "simCaloStage2Digis",
    name = "L1EmulTau",
)

l1EmulJetTable = l1JetTable.clone(
    src = "simCaloStage2Digis",
    name = "L1EmulJet",
)

l1EmulEtSumTable = l1EtSumTable.clone(
    src = "simCaloStage2Digis",
    name = "L1EmulEtSum",
)

l1EmulAK4CTJet0Table = l1JetTable.clone(
    src = 'l1sAK4CTJets0Emu',
    name = 'L1EmulAK4CTJet0',
    variables = cms.PSet(
        l1P3Vars,
        mass = Var("mass", float, precision=l1_float_precision_)
    )
)

l1EmulAK4CTJet0CorrTable = l1EmulAK4CTJet0Table.clone(
    src = 'l1sAK4CTJets0EmuCorr',
    name = 'L1EmulAK4CTJet0Corr'
)

l1EmulAK4CTJet1Table = l1EmulAK4CTJet0Table.clone(
    src = 'l1sAK4CTJets1Emu',
    name = 'L1EmulAK4CTJet1'
)

##
## Tasks
##
l1EmulCaloLayer1NanoTask = cms.Task(
    l1EmulCaloTowerTable,
    l1EmulCaloClusterTable
)

l1EmulObjTablesTask = cms.Task(
    l1EmulMuTable,
    l1EmulEGTable,
    l1EmulTauTable,
    l1EmulJetTable,
    l1EmulEtSumTable,
    l1EmulAK4CTJet0Table,
    l1EmulAK4CTJet0CorrTable,
    l1EmulAK4CTJet1Table,
)
