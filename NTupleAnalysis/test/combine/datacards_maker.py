#!/usr/bin/env python3
import argparse
import ROOT

from pathlib import Path

def is_signal_process(process):
    return process.startswith('ZprimeToQQ_M')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Script to create datacards (text and ROOT files) to be used with combine',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-i', '--fileNames', nargs='+', type=str, required=True,
        help='List of files containing input histograms')

    parser.add_argument('-e', '--extra-norm-factors', nargs='+', type=int, default=[1, 10, 30, 60, 120],
        help='List of extra normalisation factors to all histograms')

    parser.add_argument('-l', '--luminosity-ipb', type=float, required=True,
        help='Integrated luminosity of data histograms in inverse picobarns')

    parser.add_argument('-n', '--input-hist-norm', default='eventsProcessed',
        help='Name of input histogram once integral is used to normalize MC histograms')

    parser.add_argument('-d', '--data-label', default='data_obs',
        help='Name of histogram for real data in the output files')

    parser.add_argument('-f', '--fake-bkg', action='store_true', default=False,
        help='Force "bkg" histogram to be a copy of the corresponding data histogram')

    args = parser.parse_args()

    input_files = sorted(list(set(args.fileNames)))

    input_hist_norm = args.input_hist_norm

    fake_bkg = args.fake_bkg

    lumi_label = f'{args.luminosity_ipb:05.1f}'.replace('.', 'p') + 'pb'
    lumi_val_nb = args.luminosity_ipb * 1e3

    extra_norm_factors = sorted(list(set(args.extra_norm_factors)))

    data_label = args.data_label

    process_names = {
        'L1ScoutingSelection_Run2026D': data_label,
        'ZprimeToQQ_M200_TuneCP5_13p6TeV_pythia8': 'ZPqq200',
        'ZprimeToQQ_M300_TuneCP5_13p6TeV_pythia8': 'ZPqq300',
        'ZprimeToQQ_M400_TuneCP5_13p6TeV_pythia8': 'ZPqq400',
        'ZprimeToQQ_M500_TuneCP5_13p6TeV_pythia8': 'ZPqq500',
    }

    channel_labels = [
        'L1SCaloJet_Std_Mjj150',
        'L1SCaloJet_Std_Mjj150dY1p1dPhi1p0',
        'L1SCaloJet_Cmb_Mjj150',
        'L1SCaloJet_Cmb_Mjj150dY1p1dPhi1p0',

        'L1TJet_Std_Mjj150',
        'L1TJet_Std_Mjj150dY1p1dPhi1p0',
        'L1TJet_Cmb_Mjj150',
        'L1TJet_Cmb_Mjj150dY1p1dPhi1p0',
    ]

    channel_labels = sorted(list(set(channel_labels)))

    for extra_norm_fac in extra_norm_factors:

        apply_extra_norm_fac = bool(extra_norm_fac > 1)
        extra_label = f'_extraFac{extra_norm_fac:03d}' if apply_extra_norm_fac else ''

        for channel_label in channel_labels:

            input_hist_name = f'{channel_label}_J1J2_mass'

            output_file_name = f'datacard_L{lumi_label}_{channel_label}{extra_label}.root'
            print(output_file_name)

            ofile = ROOT.TFile(output_file_name, 'recreate')

            for input_file in input_files:

                process_key = Path(input_file).stem
                process_name = process_names[process_key]
                is_data = process_name == data_label
                is_signal = is_signal_process(process_key)

                output_hist_name = f'{channel_label}__{process_name}'
                print(f'  {output_hist_name}')

                ifile = ROOT.TFile.Open(input_file)
                inph = ifile.Get(input_hist_name)

                outh = inph.Clone()
                outh.SetName(output_hist_name)

                if not is_data:
                    outh_norm = ifile.Get(input_hist_norm).Integral()
                    if outh_norm <= 0:
                        raise RuntimeError(f'normalization for MC output histogram is zero: {input_file}:{input_hist_norm}')
                    outh.Scale(lumi_val_nb / outh_norm)

                if apply_extra_norm_fac:
                    outh.Scale(extra_norm_fac)

                ofile.cd()
                outh.Write()

                if fake_bkg and is_data:
                    outh2 = outh.Clone()
                    output_hist_name2 = output_hist_name.replace(data_label, 'bkg')
                    outh2.SetName(f'{output_hist_name2}')
                    print(f'  {output_hist_name2}')
                    outh2.Write()

                if is_signal:
                    with open(f'{output_file_name[:-5]}_{process_name}.txt', 'w') as dfile:
                        dfile.write(f"""\
imax   *   number of categories
jmax   *   number of samples minus one
kmax   *   number of nuisance parameter
---------------------------------------------------------------------------------------------------------------------

shapes  *  *  {output_file_name}  $CHANNEL__$PROCESS  $CHANNEL__$PROCESS__$SYSTEMATIC
---------------------------------------------------------------------------------------------------------------------

bin          {channel_label}
observation  -1
---------------------------------------------------------------------------------------------------------------------

bin      {channel_label} {channel_label}
process  {process_name}  bkg
process  0               1
rate     -1              -1
---------------------------------------------------------------------------------------------------------------------
#Source of uncertainty   pdf   {process_name}  bkg
lumi                     lnN   1.01            -

# [channel] autoMCStats [gauss/poisson threshold] [include-signal = 0] [hist-mode = 1]
#* autoMCStats 0 0 1
""")

                ifile.Close()

        ofile.Close()
