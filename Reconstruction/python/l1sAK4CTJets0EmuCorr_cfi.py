import FWCore.ParameterSet.Config as cms

from L1ScoutingTools.Reconstruction.L1TCaloTowerJetCorrector import L1TCaloTowerJetCorrector

l1sAK4CTJets0EmuCorr = L1TCaloTowerJetCorrector(
    src = 'l1sAK4CTJets0Emu',
    puProxy = 'l1sCTMultAbsIEta4',
    jecFile = 'L1ScoutingTools/Reconstruction/data/JEC_AK4CaloTowerL1S_Run3Winter25_v1.txt',
    bxMin = 0,
    bxMax = 0
)
