import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

# https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/EXO-RunIIFall18GS-01882/0
# https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/EXO-RunIII2024Summer24GS-01400/0
# https://gitlab.cern.ch/cms-gen/genproductions_cards/-/blob/59dd11e15f73d7db25f5b763c89b4193a4467fc5/genfragments/production/13p6TeV/RSGraviton/RSGravTo2Q_kMpl01_M_50_TuneCP5_13p6TeV_pythia8-fragment.py

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
    comEnergy = cms.double(13600.0),
    filterEfficiency = cms.untracked.double(1),
    maxEventsToPrint = cms.untracked.int32(0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
            'ExtraDimensionsG*:ffbar2G* = on', 
            'ExtraDimensionsG*:kappaMG = 0.54',
            '5100039:m0 = 450',
            '5100039:onMode = off',
            '5100039:onIfAny = 1 2 3 4 5'
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            'pythia8PSweightsSettings',
            'processParameters'
        )
    )
)

ProductionFilterSequence = cms.Sequence(generator)
