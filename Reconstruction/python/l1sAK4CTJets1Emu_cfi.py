import FWCore.ParameterSet.Config as cms

from L1ScoutingTools.Reconstruction.L1TCaloTowerAKJetProducer import L1TCaloTowerAKJetProducer

l1sAK4CTJets1Emu = L1TCaloTowerAKJetProducer(
    src = 'simCaloStage2Layer1Digis',
    bxMin = -2,
    bxMax = 2,
    towerMinHwPt = 1,
    towerMaxHwPt = 508,
    rParam = 0.4,
    jetPtMin = 5
)
