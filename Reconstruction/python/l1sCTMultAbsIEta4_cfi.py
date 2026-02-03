import FWCore.ParameterSet.Config as cms

from L1ScoutingTools.Reconstruction.L1TCaloTowerMultiplicityProducer import L1TCaloTowerMultiplicityProducer

l1sCTMultAbsIEta4 = L1TCaloTowerMultiplicityProducer(
    src = 'simCaloStage2Layer1Digis',
    bunchCrossing = 0,
    towerMinHwPt = 1,
    towerMaxHwPt = -1,
    towerMinAbsHwEta = -1,
    towerMaxAbsHwEta = 4,
)
