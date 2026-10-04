Scripts to set up batch jobs for private MC productions (tested only on HTCondor using lxplus8 nodes).

----------------------------
#### Production tag `261005`
 - First set of $Z' \rightarrow q\bar{q}$ ($q = u,d,c,s,b$) signal samples.
    - $M(Z') = 200,300,400,600$ GeV.
    - 1M events per sample.
 - Same GEN fragments as [`/ZprimeToQQ_Par-M-*_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24*-150X_mcRun3_2024_realistic_v*-v*/MINIAODSIM`](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2FZprimeToQQ_Par-M-*_TuneCP5_13p6TeV_pythia8%2FRunIII2024Summer24*-150X_mcRun3_2024_realistic_v*-v*%2FMINIAODSIM), except for the fact that in this case the $Z' \rightarrow b\bar{b}$ decays are included.
 - [GEN-SIM](https://cms-pdmv-prod.web.cern.ch/mcm/chained_requests?prepid=EXO-chain_RunIII2024Summer24GS_flowRunIII2024Summer24DRPremixNoOutput_flowRunIII2024Summer24MiniAODv6_flowRunIII2024Summer24NanoAODv15-00078) and [DIGI](https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_test/EXO-RunIII2024Summer24DRPremix-01915) steps copied from the `RunIIISummer24` campaign.
 - Last step combines RAW2DIGI with a custom NANO flavour that emulates/reconstructs L1T- and L1S-related objects (incl. AK4 CaloJets); this last step uses the same GlobalTag as the previous steps, but the `L1TCaloParams` payload corresponding to the 2025-26 L1T calorimeter calibrations (e.g. ZS thresholds for ECAL and HCAL TPs, JECs for standard L1T jets).
   - Executed using [missirol/cmssw@56ae86e9](https://github.com/missirol/cmssw/commit/56ae86e952cda71c1fa2361e378304d9d90a9c1c) (built on top of [`CMSSW_17_0_0_pre5`](https://github.com/cms-sw/cmssw/tree/CMSSW_17_0_0_pre5)) and the tag [`prod_261005`](https://github.com/missirol/cmssw-L1ScoutingTools/releases/tag/prod_261005) of this package.
----------------------------
