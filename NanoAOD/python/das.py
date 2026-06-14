#!/usr/bin/env python
"""
utilities related to the CMS Data Aggregation System (DAS)
"""
import json

from L1ScoutingTools.NanoAOD.common import *

def load_dataset_data(das_name, max_files=-1, max_events=-1, parentFiles_levels=2, files_prefix='', verbose=False):

    if verbose:
       print(colored_text(das_name, ['1']))

    dataset_split = das_name.split('/')
    if len(dataset_split) != 4:
       KILL('load_dataset_data -- invalid data-set name (format is incorrect, check slashes): '+das_name)

    dset_data = {'DAS': str(das_name), 'files': []}

    dataset_keyword = 'block' if '#' in dataset_split[3] else 'dataset'

    dataset_files = command_output_lines(f'dasgoclient --query "file {dataset_keyword}={das_name} | grep file.name,file.nevents"')
    dataset_files = [_tmp for _tmp in dataset_files if _tmp != '']
    dataset_files = sorted(list(set(dataset_files)))

    if len(dataset_files) == 0:
       KILL('load_dataset_data -- empty list of input files for dataset: '+str(das_name))

    if max_files > 0:
       dataset_files = dataset_files[:max_files]

    dataset_filesNevents = []
    for _tmp in dataset_files:
        _tmp_split = _tmp.split()
        if len(_tmp_split) != 2:
           KILL(das_name+' '+str(_tmp))
        if not is_int(_tmp_split[1]):
           KILL(das_name+' '+i_file+' '+str(_tmp_split[1]))
        dataset_filesNevents += [[_tmp_split[0], int(_tmp_split[1])]]

    totEvents, breakLoop = 0, False
    for i_file_idx, [i_file, i_file_nevents] in enumerate(dataset_filesNevents):
        totEvents += i_file_nevents
        if (max_events > 0) and (totEvents >= max_events):
           breakLoop = True

        if verbose:
           print('  [ file', i_file_idx+1, '/', len(dataset_filesNevents), '] [ # events =', i_file_nevents, ']', i_file)

        i_file_parents1 = []
        i_file_parents2 = []
        if parentFiles_levels > 0:
           i_file_parents1 = command_output_lines('dasgoclient --query "parent file='+str(i_file)+'"')
           i_file_parents1 = [files_prefix+_tmp for _tmp in i_file_parents1 if _tmp]
           i_file_parents1 = sorted(list(set(i_file_parents1)))
           if parentFiles_levels > 1:
              i_file_parents2 = []
              for i_file_aodf in i_file_parents1:
                  i_file_parents2_tmp = command_output_lines('dasgoclient --query "parent file='+str(i_file_aodf)+'"')
                  i_file_parents2_tmp = [_tmp.replace(' ', '') for _tmp in i_file_parents2_tmp]
                  i_file_parents2_tmp = [files_prefix+_tmp for _tmp in i_file_parents2_tmp if _tmp]
                  i_file_parents2_tmp = sorted(list(set(i_file_parents2_tmp)))
                  i_file_parents2 += i_file_parents2_tmp
              i_file_parents2 = sorted(list(set(i_file_parents2)))

        if verbose:
           for _tmp in i_file_parents2:
               print(' '*5, _tmp)

        dset_data['files'] += [{
          'file': files_prefix+i_file,
          'nevents': i_file_nevents,
          'parentFiles_1': i_file_parents1,
          'parentFiles_2': i_file_parents2,
        }]

        if breakLoop:
           break

    del totEvents, breakLoop

    # consistency checks on dataset data
    assert_dataset_data(dset_data=dset_data, verbose=verbose)

    return dset_data

def assert_dataset_data(dset_data, verbose=False):

    if not isinstance(dset_data, dict):
       KILL('assert_dataset_data -- invalid content of dataset .json file [-d]: '+str(file_path))

    if 'DAS' not in dset_data:
       KILL('assert_dataset_data -- 11')
    elif not isinstance(dset_data['DAS'], str):
       KILL('assert_dataset_data -- 12')

    if 'files' not in dset_data:
       KILL('assert_dataset_data -- 21')
    elif not isinstance(dset_data['files'], list):
       KILL('assert_dataset_data -- 22')

    for i_ent in dset_data['files']:

        if not isinstance(i_ent, dict):
           KILL('assert_dataset_data -- 31')

        if 'file' not in i_ent:
           KILL('assert_dataset_data -- 41 '+str(i_ent))
        elif not isinstance(i_ent['file'], str):
           KILL('assert_dataset_data -- 42 '+str(i_ent))

        if 'nevents' not in i_ent:
           KILL('assert_dataset_data -- 41 '+str(i_ent))
        elif not isinstance(i_ent['nevents'], int):
           KILL('assert_dataset_data -- 42 '+str(i_ent))
        elif i_ent['nevents'] < 0:
           KILL('assert_dataset_data -- 43 '+str(i_ent))

        for _tmp in ['parentFiles_1', 'parentFiles_2']:
            if _tmp not in i_ent:
               KILL('assert_dataset_data -- 51 '+str(i_ent))
            elif not isinstance(i_ent[_tmp], list):
               KILL('assert_dataset_data -- 52 '+str(i_ent))
            else:
               for _tmp2 in i_ent[_tmp]:
                   if not isinstance(_tmp2, str):
                      KILL('assert_dataset_data -- 53 '+str(i_ent))

def skim_das_jsondump(file_path, max_files=-1, max_events=-1, verbose=False):

    dset_data = json.load(open(file_path))

    # consistency checks on dataset data
    assert_dataset_data(dset_data, verbose=verbose)

    # skim input list based on max_files and max_events
    if max_files > 0:
       dset_data['files'] = dset_data['files'][:max_files]

    if max_events > 0:
       lastIndex, totEvents = 0, 0
       for _tmp in dset_data['files']:
           lastIndex += 1
           totEvents += _tmp['nevents']
           if totEvents >= max_events:
              break
       if lastIndex != len(dset_data['files']):
          dset_data['files'] = dset_data['files'][:lastIndex]
       del lastIndex, totEvents

    return dset_data

def load_dataset_data2(das_name, max_events=-1, parentFiles_levels=0, files_prefix='', verbose=False):

    if verbose:
        print(colored_text(das_name, ['1']))

    dataset_split = das_name.split('/')
    if len(dataset_split) != 4:
       KILL('load_dataset_data2 -- invalid data-set name (format is incorrect, check slashes): '+das_name)

    dset_data = {'DAS': str(das_name), 'files': []}

    dataset_keyword = 'block' if '#' in dataset_split[3] else 'dataset'

    das_query = f'dasgoclient --query "file,run,lumi {dataset_keyword}={das_name}"'
    dataset_fileRunLumi_output_lines = command_output_lines(das_query)
    dataset_fileRunLumi_output_lines = [_tmp for _tmp in dataset_fileRunLumi_output_lines if _tmp != '']
    dataset_fileRunLumi_output_lines = sorted(list(set(dataset_fileRunLumi_output_lines)))

    das_query2 = f'dasgoclient --query "file {dataset_keyword}={das_name} | grep file.name,file.nevents"'
    dataset_fileNEvents_output_lines = command_output_lines(das_query2)
    dataset_fileNEvents_output_lines = [_tmp for _tmp in dataset_fileNEvents_output_lines if _tmp != '']
    dataset_fileNEvents_output_lines = sorted(list(set(dataset_fileNEvents_output_lines)))

    if len(dataset_fileRunLumi_output_lines) == 0:
       KILL('load_dataset_data2 -- empty list of input files for dataset: '+str(das_name))

    if len(dataset_fileRunLumi_output_lines) != len(dataset_fileNEvents_output_lines):
       log_msg = f'load_dataset_data2 -- inconsistent output of DAS queries:'
       log_msg += f'\n     - "{das_query}" returned {len(dataset_fileRunLumi_output_lines)} unique entries.'
       log_msg += f'\n     - "{das_query2}" returned {len(dataset_fileNEvents_output_lines)} unique entries.'
       KILL(log_msg)

    dataset_fileNEvents_dict = dict()
    for dataset_fileNEvents_output_line in dataset_fileNEvents_output_lines:
        try:
            dataset_fileNEvents_output_line_split = dataset_fileNEvents_output_line.split()
            file_name = dataset_fileNEvents_output_line_split[0]
            file_nevents = int(dataset_fileNEvents_output_line_split[1])
            dataset_fileNEvents_dict[file_name] = file_nevents
        except:
            KILL(f'load_dataset_data2 -- invalid format of DAS output line (expected: "file nevents"): "{dataset_fileNEvents_output_line}"')

    for i_fileRunLumi_line in dataset_fileRunLumi_output_lines:
        i_fileRunLumi_line_split = i_fileRunLumi_line.split()

        if len(i_fileRunLumi_line_split) != 3:
            raise RuntimeError(f'invalid output for DAS query "{das_query}" (number of entries different from 3): {i_fileRunLumi_line}')

        i_file = i_fileRunLumi_line_split[0]
        i_file_run_str = i_fileRunLumi_line_split[1]
        try:
            i_file_run = int(i_file_run_str)
        except:
            raise RuntimeError(f'invalid output for DAS query "{das_query}" (run number cannot be converted to an integer): {i_file_run_str}')

        i_file_lumis_str = i_fileRunLumi_line_split[2]
        if not (i_file_lumis_str.startswith('[') and i_file_lumis_str.endswith(']')):
            raise RuntimeError(f'invalid output for DAS query "{das_query}" (invalid format for list of luminosity blocks): {i_file_lumis_str}')
        i_file_lumis = []
        for lumi_str in i_file_lumis_str[1:-1].split(','):
            i_file_lumis.append(int(lumi_str))
        i_file_lumis = sorted(list(set(i_file_lumis)))

        i_file_parents1 = []
        i_file_parents2 = []
        if parentFiles_levels > 0:
           i_file_parents1 = command_output_lines('dasgoclient --query "parent file='+str(i_file)+'"')
           i_file_parents1 = [files_prefix+_tmp for _tmp in i_file_parents1 if _tmp]
           i_file_parents1 = sorted(list(set(i_file_parents1)))
           if parentFiles_levels > 1:
              i_file_parents2 = []
              for i_file_aodf in i_file_parents1:
                  i_file_parents2_tmp = command_output_lines('dasgoclient --query "parent file='+str(i_file_aodf)+'"')
                  i_file_parents2_tmp = [_tmp.replace(' ', '') for _tmp in i_file_parents2_tmp]
                  i_file_parents2_tmp = [files_prefix+_tmp for _tmp in i_file_parents2_tmp if _tmp]
                  i_file_parents2_tmp = sorted(list(set(i_file_parents2_tmp)))
                  i_file_parents2 += i_file_parents2_tmp
              i_file_parents2 = sorted(list(set(i_file_parents2)))

        i_file_nevents = dataset_fileNEvents_dict[i_file]

        dset_data['files'] += [{
          'file': files_prefix+i_file,
          'run': i_file_run,
          'lumis': i_file_lumis,
          'nevents': i_file_nevents,
          'parentFiles_1': i_file_parents1,
          'parentFiles_2': i_file_parents2,
        }]

        if verbose:
            print(f'  [ {i_fileRunLumi_line} ] ({i_file_nevents} events)')

    return dset_data

def expand_json_dict(json_dict):
    ret = dict()
    for run_str in json_dict:
        run = int(run_str)
        lumiset = set()
        for pair in json_dict[run_str]:
            lumiset.update(range(pair[0], pair[1] + 1))
        ret[run] = sorted(list(lumiset))

    return ret

def convert_dataset_data2(dset_data, json_file_path=None, max_lumis=-1, max_events=-1, verbose=False):
    ret = dict({'DAS': dset_data['DAS'], 'lumis': []})
    json_dict = None if json_file_path is None else expand_json_dict(json.load(open(json_file_path)))

    for ent in dset_data['files']:
        if json_dict is not None and ent['run'] not in json_dict:
            continue

        for i_file_lumi in ent['lumis']:
            if json_dict is not None and i_file_lumi not in json_dict[ent['run']]:
                continue

            ret['lumis'] += [{
                'file': ent['file'],
                'run': ent['run'],
                'lumi': i_file_lumi,
                'nevents': ent['nevents'],
                'parentFiles_1': ent['parentFiles_1'],
                'parentFiles_2': ent['parentFiles_2'],
            }]

    ret['lumis'].sort(key=lambda x: (x['run'], x['lumi']))

    # skim input list based on max_lumis and max_events
    if max_lumis > 0:
       ret['lumis'] = ret['lumis'][:max_lumis]

    if max_events > 0:
       lastIndex, totEvents = 0, 0
       for _tmp in ret['lumis']:
           lastIndex += 1
           totEvents += _tmp['nevents']
           if totEvents >= max_events:
              break
       if lastIndex != len(ret['lumis']):
          ret['lumis'] = ret['lumis'][:lastIndex]
       del lastIndex, totEvents

    return ret
