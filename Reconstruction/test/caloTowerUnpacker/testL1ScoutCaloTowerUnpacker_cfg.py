"""
Configuration file to process L1-Scouting FRD with cmsRun
unpacking CaloTower data, and running jet clustering on CaloTowers

Original Author: Rocco Ardino (CERN)
"""
import FWCore.ParameterSet.Config as cms

import argparse
import glob
import os

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-r', '--runNumber', type=int, default=None, required=True,
    help='Run number of input files')

parser.add_argument('-n', '--maxEvents', type=int, default=-1,
    help='Value of process.maxEvents.input')

parser.add_argument('-t', '--nThreads', type=int, default=1,
    help='Value of process.options.numberOfThreads')

parser.add_argument('-s', '--nStreams', type=int, default=0,
    help='Value of process.options.numberOfStreams')

parser.add_argument('-e', '--reportEvery', type=int, default=1,
    help='Value of process.MessageLogger.cerr.FwkReport.reportEvery')

parser.add_argument('--repeat', type=int, default=1,
    help='Number of times that the input events are processed')

parser.add_argument('-j', '--jet-clustering', action=argparse.BooleanOptionalAction, default=True,
    help='Run (or not) jet-clustering on CaloTowers using FastJet')

parser.add_argument('-o', '--outputFile', type=str, default=None,
    help='Path to EDM output file (if not specified, no output is created)')

args = parser.parse_args()

runNum = args.runNumber

buBaseDir = '.'
baseDir = './tmp'

inputFileNamesPattern = f'{buBaseDir}/run{str(runNum).zfill(6)}/run*_ls*_index*.raw'
inputFileNames = glob.glob(inputFileNamesPattern)
inputFileNames = sorted(list(set(inputFileNames)))

if not inputFileNames:
    raise SystemExit(f">>> Fatal Error - found zero valid input files: {inputFileNamesPattern}")

try:
    os.remove(baseDir)
    os.makedirs(f'{baseDir}/run{str(runNum).zfill(6)}')
except:
    pass

process = cms.Process('SCPU')

process.maxEvents.input = args.maxEvents

process.options.numberOfThreads = args.nThreads
process.options.numberOfStreams = args.nStreams

# ShmStreamConsumer requires synchronization at LuminosityBlock boundaries
process.options.numberOfConcurrentLuminosityBlocks = 1

process.MessageLogger.cerr.FwkReport.reportEvery = args.reportEvery
process.MessageLogger.FastReport = cms.untracked.PSet()

from EventFilter.Utilities.EvFDaqDirector import EvFDaqDirector
process.EvFDaqDirector = EvFDaqDirector(
    buBaseDirsAll = [baseDir],
    buBaseDirsNumStreams = [1],
    fileBrokerHost = 'htcp40.cern.ch',
    runNumber = runNum,
    baseDir = baseDir,
    buBaseDir = buBaseDir
)

from EventFilter.Utilities.DAQSource import DAQSource
process.source = DAQSource(
    testing = cms.untracked.bool(True),
    dataMode = 'ScoutingRun3',
    verifyChecksum = False,
    maxChunkSize = 2048,
    eventChunkSize = 2048,
    eventChunkBlock = 1024,
    fileListMode = True,
    fileNames = (inputFileNames * args.repeat)
)

from HLTrigger.Timer.FastTimerService import FastTimerService
process.FastTimerService = FastTimerService(
    printRunSummary = False,
    enableDQM = False,
)

from EventFilter.L1ScoutingRawToDigi.ScCaloTowerRawToDigi import ScCaloTowerRawToDigi
process.l1sCaloTowers = ScCaloTowerRawToDigi(
    debug = False
)

process.p = cms.Path(process.l1sCaloTowers)

if args.jet_clustering:
    from L1TriggerScouting.OnlineProcessing.ScoutingJetProducer import ScoutingJetProducer
    process.l1sAK4CaloTowerJets = ScoutingJetProducer(
        src = 'l1sCaloTowers:CaloTower',
        akR = 0.4,
        ptMin = 5.0,
    )
    process.p += process.l1sAK4CaloTowerJets

if args.outputFile is not None:
    process.outputModule = cms.OutputModule('PoolOutputModule',
        fileName = cms.untracked.string(f'{args.outputFile}'),
        outputCommands = cms.untracked.vstring(
            'keep *',
            'drop *_rawDataCollector_*_*',
            'keep *_l1sCaloTowers_*_*',
            'keep *_l1sAK4CaloTowerJets_*_*',
        )
    )
    process.ep = cms.EndPath(process.outputModule)

from Validation.Performance.TimeMemoryJobReport import customiseWithTimeMemoryJobReport
process = customiseWithTimeMemoryJobReport(process)
