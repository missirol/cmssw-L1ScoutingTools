import FWCore.ParameterSet.Config as cms

import argparse
import os
import re

parser = argparse.ArgumentParser(
    description = 'Convert a set of Scouting Raw Data (SRD) files into one EDM file',
    formatter_class = argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('-i', '--inputDirName', type=str, required=True,
    help='Path to directory containing the SRD files (e.g. /tmp/run123456/)')

parser.add_argument('-o', '--outputFileName', type=str, required=True,
    help='Output file name')

parser.add_argument('-n', '--maxEvents', type=int, default=-1,
    help='Value of process.maxEvents.input')

parser.add_argument('--reportEvery', type=int, default=1,
    help='Value of process.MessageLogger.cerr.FwkReport.reportEvery')

parser.add_argument('-l', '--lumiSections', nargs='+', type=int, default=[],
    help='List of luminosity sections to be processed'
         ' (if no value is specified, this parameter is ignored)')

parser.add_argument('--baseDir', type=str, default='./tmp',
    help='Value of process.EvFDaqDirector.baseDir')

parser.add_argument('--buBaseDir', type=str, default='.',
    help='Value of process.EvFDaqDirector.buBaseDir')

parser.add_argument('--buBaseDirsNumStreams', nargs='+', type=int, default=[29],
    help='Value of process.EvFDaqDirector.buBaseDirsNumStreams')

parser.add_argument('--repeat', type=int, default=1,
    help='Number of times that the input events are processed,'
         ' to inflate the number of events in the output file')

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

if os.path.exists(args.outputFileName):
    raise SystemExit(f'>>> Fatal Error - target output file already exists: {args.outputFileName}')

if args.repeat < 1:
    raise SystemExit(f'>>> Fatal Error - invalid value for the "repeat" parameter: {args.repeat}')

try:
    os.makedirs(f'{args.baseDir}/run{runNumber:06d}')
except Exception as ex:
    pass

process = cms.Process("REPACK")

process.maxEvents.input = args.maxEvents

process.options.numberOfThreads = 1
process.options.numberOfStreams = 0

process.MessageLogger.cerr.FwkReport.reportEvery = args.reportEvery

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
    dataMode = 'ScoutingRun3',
    maxChunkSize = 2048,
    eventChunkSize = 2048,
    eventChunkBlock = 1024,
    fileListMode = True,
    fileNames = (fileNames * args.repeat)
)

from IOPool.Output.PoolOutputModule import PoolOutputModule
process.outputModule = PoolOutputModule(
    fileName = args.outputFileName
)

process.outputEndPath = cms.EndPath(process.outputModule)
