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
                    help='Run number')

parser.add_argument('-o', '--outputFile', type=str, default=None, required=True,
                    help='Path to EDM output file')

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

process.maxEvents.input = -1

process.options.numberOfThreads = 1
process.options.numberOfStreams = 0

# ShmStreamConsumer requires synchronization at LuminosityBlock boundaries
process.options.numberOfConcurrentLuminosityBlocks = 1

process.MessageLogger.cerr.FwkReport.reportEvery = 1

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
    fileNames = inputFileNames
)

from EventFilter.L1ScoutingRawToDigi.ScCaloTowerRawToDigi import ScCaloTowerRawToDigi
process.l1sCaloTowerUnpacker = ScCaloTowerRawToDigi(
  sourceIdList = [32],
  debug = False
)

from L1TriggerScouting.OnlineProcessing.ScoutingJetProducer import ScoutingJetProducer
process.l1sFastJetProducer = ScoutingJetProducer(
  src = 'l1sCaloTowerUnpacker:CaloTower',
  akR = 0.4,
  ptMin = 5.0,
  debug = False
)

process.output = cms.OutputModule('PoolOutputModule',
    fileName = cms.untracked.string(f'{args.outputFile}'),
    outputCommands = cms.untracked.vstring(
        'keep *',
        'drop *_rawDataCollector_*_*',
        'keep *_l1sCaloTowerUnpacker_*_*',
        'keep *_l1sFastJetProducer_*_*',
    )
)

process.p = cms.Path(
    process.l1sCaloTowerUnpacker
  + process.l1sFastJetProducer
)

process.ep = cms.EndPath(process.output)
