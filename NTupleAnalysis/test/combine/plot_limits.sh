#!/bin/bash

# L1T vs L1S
python3 plot_limits.py "${1}" -c \
     L005p6pb_L1TJet_Std_Mjj150 \
     L005p6pb_L1SCaloJet_Std_Mjj150 \
     L005p6pb_L1TJet_Std_Mjj150dY1p1dPhi1p0 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0 \
  --legend-labels \
     'L1T Jets (Mjj150)' \
     'L1S CaloJets (Mjj150)' \
     'L1T Jets (Mjj150, |#Deltay|<1.1, |#Delta#phi|>1.0)' \
     'L1S CaloJets (Mjj150, |#Deltay|<1.1, |#Delta#phi|>1.0)' \
  --legend-pos 0.30 0.70 0.95 0.89 \
  --top-left '#bf{} #it{}' \
  --top-right '5.6 pb^{-1} (13.6 TeV)' \
  --text '|#eta_{jet}| < 1.1' \
  --logy \
  -o limits_plot01

# L1S projections
python3 plot_limits.py "${1}" -c \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0_extraFac005 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0_extraFac010 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0_extraFac030 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0_extraFac060 \
     L005p6pb_L1SCaloJet_Std_Mjj150dY1p1dPhi1p0_extraFac120 \
  --legend-labels \
     'X = 1' \
     'X = 5' \
     'X = 10' \
     'X = 30' \
     'X = 60' \
     'X = 120' \
  --legend-pos 0.75 0.65 0.95 0.89 \
  --top-left '#bf{} #it{}' \
  --top-right 'X #times 5.6 pb^{-1} (13.6 TeV)' \
  --text 'L1S CaloJets (Mjj150, |#Deltay|<1.1, |#Delta#phi|>1.0)' \
  --logy \
  -o limits_plot02

# L1T Jet
python3 plot_limits.py "${1}" -c \
     L005p6pb_L1TJet_Std_Mjj150dY1p1dPhi1p0 \
     L005p6pb_L1TJet_Std_Mjj150dY1p1dPhi1p0_extraFac005 \
  --legend-labels \
     'X = 1' \
     'X = 5' \
  --legend-pos 0.75 0.65 0.95 0.89 \
  --top-left '#bf{} #it{}' \
  --top-right 'X #times 5.6 pb^{-1} (13.6 TeV)' \
  --text 'L1T Jets (Mjj150, |#Deltay|<1.1, |#Delta#phi|>1.0)' \
  --logy \
  -o limits_plot03
