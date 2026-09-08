import FWCore.ParameterSet.Config as cms

import argparse
import glob
import os

parser = argparse.ArgumentParser(
    description = 'Config to run the main L1-Scouting modules on EDM files containing'
                  ' raw data from the L1-Scouting FEDs (SDSRawDataCollection)',
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-i', '--fileNames', nargs='+', type=str, required=True,
    help='Value of process.source.fileNames')

parser.add_argument('-o', '--outputFileNamePrefix', type=str, default=None,
    help='Prefix of the name of the output files (if not specified, no OutputModule will run)')

parser.add_argument('-n', '--maxEvents', type=int, default=-1,
    help='Value of process.maxEvents.input')

parser.add_argument('--reportEvery', type=int, default=1,
    help='Value of process.MessageLogger.cerr.FwkReport.reportEvery')

parser.add_argument('-t', '--numThreads', type=int, default=1,
    help='Value of process.options.numberOfThreads')

parser.add_argument('-s', '--numStreams', type=int, default=0,
    help='Value of process.options.numberOfStreams')

parser.add_argument('-e', '--eventsToProcess', nargs='+', type=str, default=[],
    help='Value of process.source.eventsToProcess')

parser.add_argument('-f', '--fastTimerService', action='store_true', default=False,
    help='Add an instance of the FastTimerService')

parser.add_argument('--noDuplicateCheck', action='store_true', default=False,
    help='Set process.source.duplicateCheckMode = "noDuplicateCheck"')

parser.add_argument('-d', '--debugModules', nargs='+', type=str, default=[],
    help='Value of Add an instance of the FastTimerService')

args = parser.parse_args()

fileNames = []
for fname in args.fileNames:
    fname_files = glob.glob(fname)
    for fname_file in fname_files:
        fname_file_str = f'file:{fname_file}' if os.path.isfile(fname_file) else fname_file
        fileNames += [fname_file_str]

fileNames = sorted(list(set(fileNames)))

if not fileNames:
    raise SystemExit(f'>>> Fatal Error - found zero input files with a valid name: {args.inputDirName}')

process = cms.Process('TEST')

process.maxEvents.input = args.maxEvents

process.options.numberOfThreads = args.numThreads
process.options.numberOfStreams = args.numStreams
# ShmStreamConsumer requires synchronization at LuminosityBlock boundaries
process.options.numberOfConcurrentLuminosityBlocks = 1

process.MessageLogger.cerr.FwkReport.reportEvery = args.reportEvery

from IOPool.Input.PoolSource import PoolSource
process.source = PoolSource(
    fileNames = fileNames
)

if args.noDuplicateCheck:
    process.source.duplicateCheckMode = 'noDuplicateCheck'

if args.eventsToProcess:
    process.source.eventsToProcess = args.eventsToProcess

import EventFilter.L1ScoutingRawToDigi.ScGMTRawToDigi_cfi
process.l1ScGmtUnpacker = EventFilter.L1ScoutingRawToDigi.ScGMTRawToDigi_cfi.ScGmtUnpacker.clone()

import EventFilter.L1ScoutingRawToDigi.ScCaloRawToDigi_cfi
process.l1ScCaloUnpacker = EventFilter.L1ScoutingRawToDigi.ScCaloRawToDigi_cfi.ScCaloUnpacker.clone()

import EventFilter.L1ScoutingRawToDigi.ScBMTFRawToDigi_cfi
process.l1ScBMTFUnpacker = EventFilter.L1ScoutingRawToDigi.ScBMTFRawToDigi_cfi.ScBMTFUnpacker.clone()

#from EventFilter.L1ScoutingRawToDigi.ScGMTRawToDigi import ScGMTRawToDigi
#process.l1ScGmtUnpacker = ScGMTRawToDigi()
#
#from EventFilter.L1ScoutingRawToDigi.ScCaloRawToDigi import ScCaloRawToDigi
#process.l1ScCaloUnpacker = ScCaloRawToDigi()
#
#from EventFilter.L1ScoutingRawToDigi.ScBMTFRawToDigi import ScBMTFRawToDigi
#process.l1ScBMTFUnpacker = ScBMTFRawToDigi()

from EventFilter.L1ScoutingRawToDigi.ScCaloTowerRawToDigi import ScCaloTowerRawToDigi
process.l1ScCaloTowerUnpacker = ScCaloTowerRawToDigi()

from L1TriggerScouting.OnlineProcessing.ScoutingJetProducer import ScoutingJetProducer
process.l1ScAK4CaloTowerJets = ScoutingJetProducer(
    src = 'l1ScCaloTowerUnpacker:CaloTower',
    akR = 0.4,
    ptMin = 0.5
)

process.L1SUnpackingSequence = cms.Sequence(
    process.l1ScGmtUnpacker
  + process.l1ScCaloUnpacker
  + process.l1ScBMTFUnpacker
  + process.l1ScCaloTowerUnpacker
)

process.L1SReconstructionSequence = cms.Sequence(
    process.l1ScAK4CaloTowerJets
)

process.L1ScoutingPath = cms.Path(
    process.L1SUnpackingSequence
  + process.L1SReconstructionSequence
)

process.DijetEt30 = cms.EDProducer("JetBxSelector",
    jetsTag          = cms.InputTag("l1ScCaloUnpacker", "Jet"),
    minNJet          = cms.int32(2),
    minJetEt         = cms.vdouble(30, 30),
    maxJetEta        = cms.vdouble(99.9, 99.9)
)

process.HMJetMult4Et20 = cms.EDProducer("JetBxSelector",
    jetsTag          = cms.InputTag("l1ScCaloUnpacker", "Jet"),
    minNJet          = cms.int32(4),
    minJetEt         = cms.vdouble(20, 20, 20, 20),
    maxJetEta        = cms.vdouble(99.9, 99.9, 99.9, 99.9),
)

process.SingleMuPt0BMTF = cms.EDProducer("MuBxSelector",
    muonsTag         = cms.InputTag("l1ScGmtUnpacker",  "Muon"),
    minNMu           = cms.int32(1),
    minMuPt          = cms.vdouble(0.0),
    maxMuEta         = cms.vdouble(99.9),
    minMuTfIndex     = cms.vint32(36),
    maxMuTfIndex     = cms.vint32(71),
    minMuHwQual    = cms.vint32(0),
)

process.DoubleMuPt0Qual8 = cms.EDProducer("MuBxSelector",
    muonsTag         = cms.InputTag("l1ScGmtUnpacker",  "Muon"),
    minNMu           = cms.int32(2),
    minMuPt        = cms.vdouble(0, 0),
    maxMuEta       = cms.vdouble(99.9, 99.9),
    minMuTfIndex     = cms.vint32(0, 0),
    maxMuTfIndex     = cms.vint32(107, 107),
    minMuHwQual      = cms.vint32(8, 8),
)

process.MuTagJetEt30Dr0p4 = cms.EDProducer("MuTagJetBxSelector",
    muonsTag         = cms.InputTag("l1ScGmtUnpacker",  "Muon"),
    jetsTag          = cms.InputTag("l1ScCaloUnpacker", "Jet"),
    minNJet          = cms.int32(1),
    minJetEt         = cms.vdouble(30),
    maxJetEta        = cms.vdouble(99.9),
    minMuPt          = cms.vdouble(0),
    maxMuEta         = cms.vdouble(99.9),
    minMuTfIndex     = cms.vint32(0),
    maxMuTfIndex     = cms.vint32(107),
    minMuHwQual      = cms.vint32(8),
    maxDR            = cms.vdouble(0.4),
)

process.Stubs3BxWindowWheelCond = cms.EDProducer("BMTFStubMultiBxSelector",
    stubsTag         = cms.InputTag("l1ScBMTFUnpacker", "BMTFStub"),
    condition        = cms.string("wheel"),
    bxWindowLength   = cms.uint32(3),
    minNBMTFStub     = cms.uint32(2)
)

process.FinalBxSelector = cms.EDFilter("FinalBxSelector",
    analysisLabels = cms.VInputTag(
        cms.InputTag("DijetEt30", "SelBx"),
        cms.InputTag("SingleMuPt0BMTF", "SelBx"),
        cms.InputTag("DoubleMuPt0Qual8", "SelBx"),
        cms.InputTag("HMJetMult4Et20", "SelBx"),
        cms.InputTag("MuTagJetEt30Dr0p4", "SelBx"),
        cms.InputTag("Stubs3BxWindowWheelCond", "SelBx")
    ),
)

# Final collection producers
process.FinalBxSelectorMuon = cms.EDProducer("MaskOrbitBxScoutingMuon",
    dataTag = cms.InputTag("l1ScGmtUnpacker",  "Muon"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("Muon")
)

process.FinalBxSelectorJet = cms.EDProducer("MaskOrbitBxScoutingJet",
    dataTag = cms.InputTag("l1ScCaloUnpacker",  "Jet"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("Jet")
)

process.FinalBxSelectorEGamma = cms.EDProducer("MaskOrbitBxScoutingEGamma",
    dataTag = cms.InputTag("l1ScCaloUnpacker",  "EGamma"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("EGamma")
)

process.FinalBxSelectorTau = cms.EDProducer("MaskOrbitBxScoutingTau",
    dataTag = cms.InputTag("l1ScCaloUnpacker",  "Tau"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("Tau")
)

process.FinalBxSelectorBxSums = cms.EDProducer("MaskOrbitBxScoutingBxSums",
    dataTag = cms.InputTag("l1ScCaloUnpacker",  "EtSum"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("EtSum")
)

process.FinalBxSelectorBMTFStub = cms.EDProducer("MaskOrbitBxScoutingBMTFStub",
    dataTag = cms.InputTag("l1ScBMTFUnpacker",  "BMTFStub"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("BMTFStub")
)

process.FinalBxSelectorCaloTower = cms.EDProducer("MaskOrbitBxScoutingCaloTower",
    dataTag = cms.InputTag("l1ScCaloTowerUnpacker",  "CaloTower"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("CaloTower")
)

process.FinalBxSelectorFastJet = cms.EDProducer("MaskOrbitBxScoutingFastJet",
    dataTag = cms.InputTag("l1ScAK4CaloTowerJets",  "FastJet"),
    selectBxs = cms.InputTag("FinalBxSelector", "SelBx"),
    productLabel = cms.string("FastJet")
)

process.bxSelectors = cms.Sequence(
    process.DijetEt30 +
    process.HMJetMult4Et20 +
    process.SingleMuPt0BMTF +
    process.DoubleMuPt0Qual8 +
    process.MuTagJetEt30Dr0p4 +
    process.Stubs3BxWindowWheelCond
)
process.MaskedCollections = cms.Sequence(
    process.FinalBxSelectorMuon +
    process.FinalBxSelectorJet +
    process.FinalBxSelectorEGamma +
#   process.FinalBxSelectorTau +
    process.FinalBxSelectorBxSums +
    process.FinalBxSelectorBMTFStub +
    process.FinalBxSelectorCaloTower +
    process.FinalBxSelectorFastJet
)

process.pL1ScoutingSelected = cms.Path(
    process.L1SUnpackingSequence
  + process.bxSelectors
  + process.FinalBxSelector
  + process.MaskedCollections
)

if args.outputFileNamePrefix:
    from IOPool.Output.PoolOutputModule import PoolOutputModule
    process.l1sOutputModule = PoolOutputModule(
        fileName = f'{args.outputFileNamePrefix}_ZeroBias.root',
        outputCommands = [
            'drop *',
            'keep *_l1ScGmtUnpacker_*_*',
            'keep *_l1ScCaloUnpacker_*_*',
            'keep *_l1ScBMTFUnpacker_*_*',
            'keep *_l1ScCaloTowerUnpacker_*_*',
            'keep *_l1ScAK4CaloTowerJets_*_*'
        ]
    )
    process.L1ScoutingOutputEndPath = cms.EndPath(process.l1sOutputModule)

    process.hltOutputL1ScoutingSelection = PoolOutputModule(
        fileName = f'{args.outputFileNamePrefix}_Selection.root',
        SelectEvents = cms.untracked.PSet(
            SelectEvents = cms.vstring("pL1ScoutingSelected")
        ),
        outputCommands = [
            'drop *',
            'keep *_DijetEt30_*_*',
            'keep *_HMJetMult4Et20_*_*',
            'keep *_SingleMuPt0BMTF_*_*',
            'keep *_DoubleMuPt0Qual8_*_*',
            'keep *_MuTagJetEt30Dr0p4_*_*',
            'keep *_Stubs3BxWindowWheelCond_*_*',
            'keep *_FinalBxSelector*_*_*',
        ]
    )
    process.epL1ScoutingSelection = cms.EndPath(process.hltOutputL1ScoutingSelection)

if args.fastTimerService:
    from HLTrigger.Timer.FastTimerService import FastTimerService
    process.FastTimerService = FastTimerService(
        printRunSummary = False,
        enableDQM = False
    )
    process.MessageLogger.FastReport = cms.untracked.PSet()

if args.debugModules:
    process.MessageLogger.cerr.threshold = 'DEBUG'
    process.MessageLogger.debugModules = args.debugModules
