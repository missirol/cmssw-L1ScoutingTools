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

parser.add_argument('-o', '--outputFileName', type=str, required=True,
    help='Output file name')

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

if os.path.exists(args.outputFileName):
    raise SystemExit(f'>>> Fatal Error - target output file already exists: {args.outputFileName}')

process = cms.Process("TEST")

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
    ptMin = 1
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

from IOPool.Output.PoolOutputModule import PoolOutputModule
process.l1sOutputModule = PoolOutputModule(
    fileName = args.outputFileName,
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
