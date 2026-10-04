import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8ConcurrentGeneratorFilter",
        comEnergy = cms.double(13600.0),
        maxEventsToPrint = cms.untracked.int32(1),
        pythiaHepMCVerbosity = cms.untracked.bool(False),
        pythiaPylistVerbosity = cms.untracked.int32(1),
        PythiaParameters = cms.PSet(
            pythia8CommonSettingsBlock,
            pythia8CP5SettingsBlock,
            pythia8PSweightsSettingsBlock,
            processParameters = cms.vstring(
                'NewGaugeBoson:ffbar2gmZZprime = on',
                'Zprime:gmZmode = 3',
                '32:m0 = 400.0', # mass of Z'
                '32:mMin = 1.0',
                '32:mWidth = 0.001',
                '32:doForceWidth = on',
                '32:onMode = off', # switch OFF all Z' decays
                '32:onIfAny = 1 2 3 4 5', # switch ON Z' to qq for q = u,d,s,c,b
            ),
            parameterSets = cms.vstring(
                'pythia8CommonSettings',
                'pythia8CP5Settings',
                'pythia8PSweightsSettings',
                'processParameters'
            )
        )
)
