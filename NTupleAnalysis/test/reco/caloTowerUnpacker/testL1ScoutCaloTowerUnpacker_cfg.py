"""
Configuration file to process L1-Scouting FRD with cmsRun
unpacking CaloTower data, and running jet clustering on CaloTowers

Original Author: Rocco Ardino (CERN)
"""
import FWCore.ParameterSet.Config as cms

import argparse
import glob
import os
import re

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-i', '--inputDirName', type=str, required=True,
    help='Path to directory containing the SRD files (e.g. /tmp/run123456/)')

parser.add_argument('-o', '--outputFileName', type=str, default=None,
    help='Path to EDM output file (if not specified, no output is created)')

parser.add_argument('-n', '--maxEvents', type=int, default=-1,
    help='Value of process.maxEvents.input')

parser.add_argument('-e', '--reportEvery', type=int, default=1,
    help='Value of process.MessageLogger.cerr.FwkReport.reportEvery')

parser.add_argument('-l', '--lumiSections', nargs='+', type=int, default=[],
    help='List of luminosity sections to be processed'
         ' (if no value is specified, this parameter is ignored)')

parser.add_argument('-t', '--nThreads', type=int, default=1,
    help='Value of process.options.numberOfThreads')

parser.add_argument('-s', '--nStreams', type=int, default=0,
    help='Value of process.options.numberOfStreams')

parser.add_argument('--baseDir', type=str, default='./tmp',
    help='Value of process.EvFDaqDirector.baseDir')

parser.add_argument('--buBaseDir', type=str, default='.',
    help='Value of process.EvFDaqDirector.buBaseDir')

parser.add_argument('--buBaseDirsNumStreams', nargs='+', type=int, default=[1],
    help='Value of process.EvFDaqDirector.buBaseDirsNumStreams')

parser.add_argument('--repeat', type=int, default=1,
    help='Number of times that the input events are processed')

parser.add_argument('-j', '--jet-clustering', action=argparse.BooleanOptionalAction, default=True,
    help='Run (or not) jet-clustering on CaloTowers using FastJet')

args = parser.parse_args()

buBaseDirsAll = os.path.dirname(os.path.abspath(args.inputDirName))
runNumber = int(os.path.basename(os.path.abspath(args.inputDirName))[len('run'):])

fileNames = []
for fname in os.listdir(args.inputDirName):
    re_match = re.match(f'run{runNumber:06d}' + '_ls([0-9]{4})_index[0-9]{6}.raw$', fname)
    if not re_match:
        continue
    if not args.lumiSections or int(re_match.group(1)) in args.lumiSections:
        fileNames += [os.path.join(args.inputDirName, fname)]

if not fileNames:
    raise SystemExit(f'>>> Fatal Error - found zero input files with a valid name: {args.inputDirName}')

if args.repeat < 1:
    raise SystemExit(f'>>> Fatal Error - invalid value for the "repeat" parameter: {args.repeat}')

try:
    os.makedirs(f'{args.baseDir}/run{runNumber:06d}')
except Exception as ex:
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
    buBaseDirsAll = [buBaseDirsAll],
    buBaseDirsNumStreams = args.buBaseDirsNumStreams,
    runNumber = runNumber,
    baseDir = args.baseDir,
    buBaseDir = args.buBaseDir
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
    fileNames = (fileNames * args.repeat)
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

if args.outputFileName:
    process.outputModule = cms.OutputModule('PoolOutputModule',
        fileName = cms.untracked.string(f'{args.outputFileName}'),
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
