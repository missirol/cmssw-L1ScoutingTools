import FWCore.ParameterSet.Config as cms

from L1ScoutingTools.Reconstruction.L1TCaloTowerJetCorrectorC import L1TCaloTowerJetCorrectorC

l1sAK4CTJets0EmuCorrC = L1TCaloTowerJetCorrectorC(
    src = 'l1sAK4CTJets0Emu',
    puProxy = 'l1sCTMultAbsIEta4',
    jecFile = 'L1ScoutingTools/Reconstruction/data/JEC_AK4CaloTowerL1S_Run3Winter25_v2.txt',
    bxMin = 0,
    bxMax = 0
)
