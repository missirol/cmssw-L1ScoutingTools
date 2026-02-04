#include <algorithm>
#include <cassert>
#include <cmath>

#include "L1ScoutingTools/NTupleAnalysis/interface/JetMETPerformanceAnalysisDriver.h"
#include "L1ScoutingTools/NTupleAnalysis/interface/Utils.h"

JetMETPerformanceAnalysisDriver::JetMETPerformanceAnalysisDriver(const std::string& tfile,
                                                                 const std::string& ttree,
                                                                 const std::string& outputFilePath,
                                                                 const std::string& outputFileMode)
    : JetMETPerformanceAnalysisDriver(outputFilePath, outputFileMode) {
  setInputTTree(tfile, ttree);
}

JetMETPerformanceAnalysisDriver::JetMETPerformanceAnalysisDriver(const std::string& outputFilePath,
                                                                 const std::string& outputFileMode)
    : AnalysisDriverBase(outputFilePath, outputFileMode) {}

void JetMETPerformanceAnalysisDriver::init() {
  jecA_.init(getOption("jecA_filePath"));

  jetCategoryLabels_ = {
      "_EtaIncl",  //"_EtaInclPt0", "_EtaInclPt1", "_EtaInclPt2", "_EtaInclPt3", "_EtaInclPt4", "_EtaInclPt5",
      "_Eta2p5",   //"_Eta2p5Pt0",  "_Eta2p5Pt1",  "_Eta2p5Pt2",  "_Eta2p5Pt3",  "_Eta2p5Pt4",  "_Eta2p5Pt5",
      "_HB",       //"_HBPt0",      "_HBPt1",      "_HBPt2",      "_HBPt3",      "_HBPt4",      "_HBPt5",
      "_HE",       //"_HEPt0",      "_HEPt1",      "_HEPt2",      "_HEPt3",      "_HEPt4",      "_HEPt5",
      "_HF",       //"_HFPt0",      "_HFPt1",      "_HFPt2",      "_HFPt3",      "_HFPt4",      "_HFPt5",

      "_HBTest0",
  };

  // histogram: events counter
  addTH1D("eventsProcessed", {0, 1});
  addTH1D("weight", 100, -5, 5);
  addTH1D("nPU", 40, 0, 120);
  addTH1D("nCT", 100, 0, 1000);
  addTH1D("nCTie4", 48, 0, 240);
  addTH2D("nPU__vs__nCT", 40, 0, 120, 100, 0, 1000);
  addTH2D("nPU__vs__nCTie4", 40, 0, 120, 48, 0, 240);

  labelMap_jetAK4_ = {
      {"GenJet", {}},
      {"GenJetNoMu",
       {{"L1T", "L1EmulJet"},
        {"L1T1", "L1EmulJet1"},
        {"L1CT0", "L1EmulAK4CTJet0"},
        {"L1CT0Corr", "L1EmulAK4CTJet0Corr"},
        {"L1CT0CorrA", "L1EmulAK4CTJet0CorrA"},
        {"L1CT1", "L1EmulAK4CTJet1"}}},
      {"L1EmulJet", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulJet1", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulAK4CTJet0", {{"GEN", "GenJetNoMu"}, {"L1T", "L1EmulJet"}}},
      {"L1EmulAK4CTJet0Corr", {{"GEN", "GenJetNoMu"}, {"L1T", "L1EmulJet"}}},
      {"L1EmulAK4CTJet0CorrA", {{"GEN", "GenJetNoMu"}, {"L1T", "L1EmulJet"}}},
      {"L1EmulAK4CTJet1", {{"GEN", "GenJetNoMu"}, {"L1T", "L1EmulJet"}}},
      {"Jet", {}},
  };

  labelMap_jetAK8_ = {};

  labelMap_MET_ = {};

  for (auto const& selLabel : {"NoSelection"}) {
    // histograms: AK4 Jets
    for (auto const& jetLabel : labelMap_jetAK4_) {
      bookHistograms_Jets(selLabel, jetLabel.first, utils::mapKeys(jetLabel.second));
    }

    //    bookHistograms_Jets_2DMaps(selLabel, "hltAK4PFJetsCorrected", "l1tSlwPFJetsCorrected");
    //    bookHistograms_Jets_2DMaps(selLabel, "hltAK4PFJetsCorrected", "offlineAK4PFJetsCorrected");

    //    bookHistograms_Jets_2DMaps(selLabel, "hltAK4PFPuppiJetsCorrected", "l1tSlwPFPuppiJetsCorrected");
    //    bookHistograms_Jets_2DMaps(selLabel, "hltAK4PFPuppiJetsCorrected", "offlineAK4PFPuppiJetsCorrected");

    //    bookHistograms_MET_2DMaps(selLabel, "hltPFPuppiHT", "l1tPFPuppiHT", true);

    // histograms: AK8 Jets
    for (auto const& jetLabel : labelMap_jetAK8_) {
      bookHistograms_Jets(selLabel, jetLabel.first, utils::mapKeys(jetLabel.second));
    }

    // histograms: MET
    for (auto const& metLabel : labelMap_MET_) {
      bookHistograms_MET(selLabel, metLabel.first, utils::mapKeys(metLabel.second));
    }

    //    bookHistograms_MET_2DMaps(selLabel, "hltPFMET", "l1tPFMET");
    //    bookHistograms_MET_2DMaps(selLabel, "hltPFMET", "offlinePFMET_Raw");
    //
    //    bookHistograms_MET_2DMaps(selLabel, "hltPFPuppiMET", "l1tPFPuppiMET");
    //    bookHistograms_MET_2DMaps(selLabel, "hltPFPuppiMET", "offlinePFPuppiMET_Raw");
    //
    //    bookHistograms_MET_2DMaps(selLabel, "hltPFPuppiMETTypeOne", "l1tPFPuppiMET");
    //    bookHistograms_MET_2DMaps(selLabel, "hltPFPuppiMETTypeOne", "offlinePFPuppiMET_Type1");
    //
    //    bookHistograms_METMHT(selLabel);
  }
}

bool JetMETPerformanceAnalysisDriver::jetBelongsToCategory(const std::string& categLabel,
                                                           const float jetPt,
                                                           const float jetAbsEta,
                                                           const unsigned int nCTie4) const {
  bool ret{false};
  if (categLabel == "_EtaIncl") {
    ret = (jetAbsEta < 5.0);
  } else if (categLabel == "_EtaInclPt0") {
    ret = (jetAbsEta < 5.0) and (30. <= jetPt) and (jetPt < 60.);
  } else if (categLabel == "_EtaInclPt1") {
    ret = (jetAbsEta < 5.0) and (60. <= jetPt) and (jetPt < 110.);
  } else if (categLabel == "_EtaInclPt2") {
    ret = (jetAbsEta < 5.0) and (110. <= jetPt) and (jetPt < 200.);
  } else if (categLabel == "_EtaInclPt3") {
    ret = (jetAbsEta < 5.0) and (200. <= jetPt) and (jetPt < 400.);
  } else if (categLabel == "_EtaInclPt4") {
    ret = (jetAbsEta < 5.0) and (400. <= jetPt) and (jetPt < 1023.4);
  } else if (categLabel == "_EtaInclPt5") {
    ret = (jetAbsEta < 5.0) and (1023.4 <= jetPt);
  }

  else if (categLabel == "_Eta2p5") {
    ret = (jetAbsEta < 2.5);
  } else if (categLabel == "_Eta2p5Pt0") {
    ret = (jetAbsEta < 2.5) and (30. <= jetPt) and (jetPt < 60.);
  } else if (categLabel == "_Eta2p5Pt1") {
    ret = (jetAbsEta < 2.5) and (60. <= jetPt) and (jetPt < 110.);
  } else if (categLabel == "_Eta2p5Pt2") {
    ret = (jetAbsEta < 2.5) and (110. <= jetPt) and (jetPt < 200.);
  } else if (categLabel == "_Eta2p5Pt3") {
    ret = (jetAbsEta < 2.5) and (200. <= jetPt) and (jetPt < 400.);
  } else if (categLabel == "_Eta2p5Pt4") {
    ret = (jetAbsEta < 2.5) and (400. <= jetPt) and (jetPt < 1023.4);
  } else if (categLabel == "_Eta2p5Pt5") {
    ret = (jetAbsEta < 2.5) and (1023.4 <= jetPt);
  }

  else if (categLabel == "_HB") {
    ret = (jetAbsEta < 1.3);
  } else if (categLabel == "_HBPt0") {
    ret = (jetAbsEta < 1.3) and (30. <= jetPt) and (jetPt < 60.);
  } else if (categLabel == "_HBPt1") {
    ret = (jetAbsEta < 1.3) and (60. <= jetPt) and (jetPt < 110.);
  } else if (categLabel == "_HBPt2") {
    ret = (jetAbsEta < 1.3) and (110. <= jetPt) and (jetPt < 200.);
  } else if (categLabel == "_HBPt3") {
    ret = (jetAbsEta < 1.3) and (200. <= jetPt) and (jetPt < 400.);
  } else if (categLabel == "_HBPt4") {
    ret = (jetAbsEta < 1.3) and (400. <= jetPt) and (jetPt < 1023.4);
  } else if (categLabel == "_HBPt5") {
    ret = (jetAbsEta < 1.3) and (1023.4 <= jetPt);

  } else if (categLabel == "_HBTest0") {
    ret = (jetAbsEta < 0.2) and (20 <= nCTie4) and (nCTie4 < 30);
  }

  else if (categLabel == "_HE") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0);
  } else if (categLabel == "_HEPt0") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (30. <= jetPt) and (jetPt < 60.);
  } else if (categLabel == "_HEPt1") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (60. <= jetPt) and (jetPt < 110.);
  } else if (categLabel == "_HEPt2") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (110. <= jetPt) and (jetPt < 200.);
  } else if (categLabel == "_HEPt3") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (200. <= jetPt) and (jetPt < 400.);
  } else if (categLabel == "_HEPt4") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (400. <= jetPt) and (jetPt < 1023.4);
  } else if (categLabel == "_HEPt5") {
    ret = (1.3 <= jetAbsEta) and (jetAbsEta < 3.0) and (1023.4 <= jetPt);
  }

  else if (categLabel == "_HF") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0);
  } else if (categLabel == "_HFPt0") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (30. <= jetPt) and (jetPt < 60.);
  } else if (categLabel == "_HFPt1") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (60. <= jetPt) and (jetPt < 110.);
  } else if (categLabel == "_HFPt2") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (110. <= jetPt) and (jetPt < 200.);
  } else if (categLabel == "_HFPt3") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (200. <= jetPt) and (jetPt < 400.);
  } else if (categLabel == "_HFPt4") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (400. <= jetPt) and (jetPt < 1023.4);
  } else if (categLabel == "_HFPt5") {
    ret = (3.0 <= jetAbsEta) and (jetAbsEta < 5.0) and (1023.4 <= jetPt);
  }

  return ret;
}

void JetMETPerformanceAnalysisDriver::analyze() {
  H1("eventsProcessed")->Fill(0.5);

  float const wgt{1.f};
  H1("weight")->Fill(wgt);

  auto const nPU = this->value<float>("Pileup_nTrueInt");
  H1("nPU")->Fill(nPU, wgt);

  auto const nCT = this->value<int>("nL1EmulCaloTower");
  H1("nCT")->Fill(nCT, wgt);

  unsigned int nCTie4{0};
  auto const& ct_ieta = this->array<int>("L1EmulCaloTower_ieta");
  for (auto idx = 0; idx < nCT; ++idx) {
    if (std::abs(ct_ieta[idx]) <= 4) {
      ++nCTie4;
    }
  }
  H1("nCTie4")->Fill(nCTie4, wgt);

  H2("nPU__vs__nCT")->Fill(nPU, nCT, wgt);
  H2("nPU__vs__nCTie4")->Fill(nPU, nCTie4, wgt);

  //// AK4 Jets
  const float minAK4JetPt{30};
  const float minAK4JetPtRef{7.5};
  const float maxAK4JetDeltaRmatchRef{0.2};

  // Single-Jet
  for (auto const& jetLabel : labelMap_jetAK4_) {
    fillHistoDataJets fhDataAK4Jets;
    fhDataAK4Jets.jetCollection = jetLabel.first;
    fhDataAK4Jets.jetPtMin = utils::stringStartsWith(jetLabel.first, "GenJet") ? minAK4JetPtRef : minAK4JetPt;
    fhDataAK4Jets.jetPtMax = (jetLabel.first == "L1EmulJet1") ? 1023.4 : -1;
    fhDataAK4Jets.jetAbsEtaMax = 5.0;
    for (auto const& jetLabelRefs : jetLabel.second) {
      auto const jetPtMin2 = utils::stringStartsWith(jetLabelRefs.second, "GenJet") ? minAK4JetPtRef : minAK4JetPt;
      auto const jetPtMax2 = (jetLabelRefs.second == "L1EmulJet1") ? 1023.4 : -1;
      fhDataAK4Jets.matches.emplace_back(fillHistoDataJets::Match(
          jetLabelRefs.first, jetLabelRefs.second, jetPtMin2, jetPtMax2, maxAK4JetDeltaRmatchRef));
    }

    fillHistograms_Jets("NoSelection", fhDataAK4Jets, wgt);

    //    if(jetLabel.first.find("l1t") == 0) continue;
    //
    //    for(auto const& selLabel : l1tSeeds_1Jet_){
    //      auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tSingleJetSeed(selLabel);
    //      if(not l1tSeed){
    //        continue;
    //      }
    //
    //      fillHistograms_Jets(selLabel, fhDataAK4Jets, wgt);
    //    }

    //    if(isGENJets) continue;
    //
    //    for(auto const& selLabel : l1tSeeds_HT_){
    //      auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tHTSeed(selLabel);
    //      if(not l1tSeed){
    //        continue;
    //      }
    //
    //      fillHistograms_Jets(selLabel, fhDataAK4Jets, wgt);
    //    }
  }

  //  // HT
  //  for(std::string const& jetType : {"PF", "PFPuppi"}){
  //
  //    fillHistoDataJets fhDataL1TSLWJets;
  //    fhDataL1TSLWJets.jetCollection = "l1tSlw"+jetType+"JetsCorrected";
  //    fhDataL1TSLWJets.jetPtMin = minAK4JetPt;
  //    fhDataL1TSLWJets.jetAbsEtaMax = 2.4;
  //
  //    fillHistoDataJets fhDataHLTAK4Jets;
  //    fhDataHLTAK4Jets.jetCollection = "hltAK4"+jetType+"JetsCorrected";
  //    fhDataHLTAK4Jets.jetPtMin = minAK4JetPt;
  //    fhDataHLTAK4Jets.jetAbsEtaMax = 5.0;
  //
  ////    fillHistoDataJets fhDataOffAK4Jets;
  ////    fhDataOffAK4Jets.jetCollection = "offlineAK4"+jetType+"JetsCorrected";
  ////    fhDataOffAK4Jets.jetPtMin = minAK4JetPt;
  ////    fhDataOffAK4Jets.jetAbsEtaMax = 5.0;
  //
  //    fillHistograms_Jets_2DMaps("NoSelection", fhDataHLTAK4Jets, fhDataL1TSLWJets, wgt);
  ////    fillHistograms_Jets_2DMaps("NoSelection", fhDataHLTAK4Jets, fhDataOffAK4Jets, wgt);
  //
  //    fillHistoDataMET fhDataHLTHT;
  //    fhDataHLTHT.metCollection = "hlt"+jetType+"HT";
  //
  //    fillHistoDataMET fhDataL1THT;
  //    fhDataL1THT.metCollection = "l1t"+jetType+"HT";
  //
  //    fillHistograms_MET_2DMaps("NoSelection", fhDataHLTHT, fhDataL1THT, true, wgt);
  //
  ////    for(auto const& selLabel : l1tSeeds_HT_){
  ////      auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tHTSeed(selLabel);
  ////      if(not l1tSeed){
  ////        continue;
  ////      }
  ////
  ////      fillHistograms_Jets_2DMaps(selLabel, fhDataHLTAK4Jets, fhDataL1TSLWJets, wgt);
  //////      fillHistograms_Jets_2DMaps(selLabel, fhDataHLTAK4Jets, fhDataOffAK4Jets, wgt);
  ////
  ////      if(jetType == "PFPuppi"){
  ////        fillHistograms_MET_2DMaps(selLabel, fhDataHLTHT, fhDataL1THT, true, wgt);
  ////      }
  ////    }
  //  }

  //  //// AK8 Jets
  //  const float minAK8JetPt(90.);
  //  const float minAK8JetPtRef(60.);
  //  const float maxAK8JetDeltaRmatchRef(0.2);
  //
  //  for(auto const& jetLabel : labelMap_jetAK8_){
  //    auto const isGENJets = (jetLabel.first.find("GenJet") != std::string::npos);
  //
  //    auto const jetPt1 = isGENJets ? minAK8JetPtRef : minAK8JetPt;
  //    auto const jetPt2 = isGENJets ? minAK8JetPtRef * 0.75 : minAK8JetPtRef;
  //
  //    fillHistoDataJets fhDataAK8Jets;
  //    fhDataAK8Jets.jetCollection = jetLabel.first;
  //    fhDataAK8Jets.jetPtMin = jetPt1;
  //    fhDataAK8Jets.jetAbsEtaMax = 5.0;
  //
  //    for(auto const& jetLabelRefs : jetLabel.second){
  //      fhDataAK8Jets.matches.emplace_back(fillHistoDataJets::Match(jetLabelRefs.first, jetLabelRefs.second, jetPt2, maxAK8JetDeltaRmatchRef));
  //    }
  //
  //    fillHistograms_Jets("NoSelection", fhDataAK8Jets, wgt);
  //  }

  //  //// MET
  //  for(auto const& metLabel : labelMap_MET_){
  //    fillHistoDataMET fhDataMET;
  //    fhDataMET.metCollection = metLabel.first;
  //    for(auto const& metRefs : metLabel.second){
  //      fhDataMET.matches.emplace_back(fillHistoDataMET::Match(metRefs.first, metRefs.second));
  //    }
  //
  //    fillHistograms_MET("NoSelection", fhDataMET, wgt);
  //
  ////    for(auto const& selLabel : l1tSeeds_MET_){
  ////      auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tMETSeed(selLabel);
  ////      if(l1tSeed){
  ////        fillHistograms_MET(selLabel, fhDataMET, wgt);
  ////      }
  ////    }
  //  }

  //  std::vector<std::vector<std::string>> metTypes({
  //    {"l1tPFMET", "hltPFMET", "offlinePFMET_Raw"},
  //    {"l1tPFPuppiMET", "hltPFPuppiMET", "offlinePFPuppiMET_Raw"},
  //    {"l1tPFPuppiMET", "hltPFPuppiMETTypeOne", "offlinePFPuppiMET_Type1"},
  //  });
  //
  //  for(auto const& metType : metTypes){
  //
  //    fillHistoDataMET fhDataL1TMET;
  //    fhDataL1TMET.metCollection = metType.at(0);
  //
  //    fillHistoDataMET fhDataHLTMET;
  //    fhDataHLTMET.metCollection = metType.at(1);
  //
  ////    fillHistoDataMET fhDataOffMET;
  ////    fhDataOffMET.metCollection = metType.at(2);
  //
  //    fillHistograms_MET_2DMaps("NoSelection", fhDataHLTMET, fhDataL1TMET, false, wgt);
  ////    fillHistograms_MET_2DMaps("NoSelection", fhDataHLTMET, fhDataOffMET, false, wgt);
  //
  //    for(auto const& selLabel : l1tSeeds_MET_){
  //      auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tMETSeed(selLabel);
  //      if(l1tSeed){
  //        fillHistograms_MET_2DMaps(selLabel, fhDataHLTMET, fhDataL1TMET, false, wgt);
  ////        fillHistograms_MET_2DMaps(selLabel, fhDataHLTMET, fhDataOffMET, false, wgt);
  //      }
  //    }
  //  }
  //
  //  //// MET+MHT
  //  fillHistograms_METMHT("NoSelection", wgt);
  //
  //  for(auto const& selLabel : l1tSeeds_MET_){
  //    auto const l1tSeed = hasTTreeReaderValue(selLabel) ? value<bool>(selLabel) : l1tMETSeed(selLabel);
  //    if(l1tSeed){
  //      fillHistograms_METMHT(selLabel, wgt);
  //    }
  //  }
}

void JetMETPerformanceAnalysisDriver::bookHistograms_Jets(const std::string& dir,
                                                          const std::string& jetType,
                                                          const std::vector<std::string>& matchLabels) {
  auto dirPrefix(dir);
  while (dirPrefix.back() == '/') {
    dirPrefix.pop_back();
  }
  if (not dirPrefix.empty()) {
    dirPrefix += "/";
  }

  std::vector<float> binEdges_njets(121);
  for (uint idx = 0; idx < binEdges_njets.size(); ++idx) {
    binEdges_njets.at(idx) = idx;
  }

  std::vector<float> binEdges_HT(221);
  for (uint idx = 0; idx < binEdges_HT.size(); ++idx) {
    binEdges_HT.at(idx) = idx * 10.;
  }

  std::vector<float> binEdges_MHT(221);
  for (uint idx = 0; idx < binEdges_MHT.size(); ++idx) {
    binEdges_MHT.at(idx) = idx * 10.;
  }

  std::vector<float> binEdges_pt(104);
  for (uint idx = 0; idx < binEdges_pt.size(); ++idx) {
    binEdges_pt.at(idx) = std::max(1.f, 10.f * idx);
  }

  std::vector<float> binEdges_eta(101);
  for (uint idx = 0; idx < binEdges_eta.size(); ++idx) {
    binEdges_eta.at(idx) = -5.0 + 0.1 * idx;
  }

  std::vector<float> binEdges_phi(41);
  for (uint idx = 0; idx < binEdges_phi.size(); ++idx) {
    binEdges_phi.at(idx) = M_PI * (0.05 * idx - 1.);
  }

  std::vector<float> const binEdges_mass(
      {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 400, 500, 600});

  std::vector<float> binEdges_numberOfDaughters(121);
  for (uint idx = 0; idx < binEdges_numberOfDaughters.size(); ++idx) {
    binEdges_numberOfDaughters.at(idx) = 2. * idx;
  }

  std::vector<float> binEdges_energyFrac(21);
  for (uint idx = 0; idx < binEdges_energyFrac.size(); ++idx) {
    binEdges_energyFrac.at(idx) = 0.05 * idx;
  }

  std::vector<float> binEdges_dauMult1(61);
  for (uint idx = 0; idx < binEdges_dauMult1.size(); ++idx) {
    binEdges_dauMult1.at(idx) = idx;
  }

  std::vector<float> binEdges_dauMult2(13);
  for (uint idx = 0; idx < binEdges_dauMult2.size(); ++idx) {
    binEdges_dauMult2.at(idx) = idx;
  }

  std::vector<float> binEdges_dRmatch(26);
  for (uint idx = 0; idx < binEdges_dRmatch.size(); ++idx) {
    binEdges_dRmatch.at(idx) = 0.2 * idx;
  }

  std::vector<float> binEdges_minDeltaR(61);
  for (uint idx = 0; idx < binEdges_minDeltaR.size(); ++idx) {
    binEdges_minDeltaR.at(idx) = 0.05 * idx;
  }

  std::vector<float> binEdges_response(101);
  for (uint idx = 0; idx < binEdges_response.size(); ++idx) {
    binEdges_response.at(idx) = 0.05 * idx;
  }

  std::vector<float> binEdges_nPU(41);
  for (uint idx = 0; idx < binEdges_nPU.size(); ++idx) {
    binEdges_nPU.at(idx) = 3 * idx;
  }

  std::vector<float> binEdges_nCTie4(49);
  for (uint idx = 0; idx < binEdges_nCTie4.size(); ++idx) {
    binEdges_nCTie4.at(idx) = 5 * idx;
  }

  for (auto const& catLabel : jetCategoryLabels_) {
    addTH1D(dirPrefix + jetType + catLabel + "_njets", binEdges_njets);
    addTH1D(dirPrefix + jetType + catLabel + "_HT", binEdges_HT);
    addTH1D(dirPrefix + jetType + catLabel + "_MHT", binEdges_MHT);
    addTH1D(dirPrefix + jetType + catLabel + "_pt", binEdges_pt);
    addTH2D(dirPrefix + jetType + catLabel + "_pt__vs__nPU", binEdges_pt, binEdges_nPU);
    addTH2D(dirPrefix + jetType + catLabel + "_pt__vs__nCTie4", binEdges_pt, binEdges_nCTie4);
    addTH1D(dirPrefix + jetType + catLabel + "_pt0", binEdges_pt);
    addTH2D(dirPrefix + jetType + catLabel + "_pt0__vs__nPU", binEdges_pt, binEdges_nPU);
    addTH2D(dirPrefix + jetType + catLabel + "_pt0__vs__nCTie4", binEdges_pt, binEdges_nCTie4);
    addTH1D(dirPrefix + jetType + catLabel + "_eta", binEdges_eta);
    addTH2D(dirPrefix + jetType + catLabel + "_eta__vs__pt", binEdges_eta, binEdges_pt);
    addTH2D(dirPrefix + jetType + catLabel + "_eta__vs__nPU", binEdges_eta, binEdges_nPU);
    addTH2D(dirPrefix + jetType + catLabel + "_eta__vs__nCTie4", binEdges_eta, binEdges_nCTie4);
    addTH1D(dirPrefix + jetType + catLabel + "_phi", binEdges_phi);
    addTH1D(dirPrefix + jetType + catLabel + "_mass", binEdges_mass);
    //    addTH1D(dirPrefix+jetType+catLabel+"_numberOfDaughters", binEdges_numberOfDaughters);
    //    addTH1D(dirPrefix+jetType+catLabel+"_chargedHadronEnergyFraction", binEdges_energyFrac);
    //    addTH1D(dirPrefix+jetType+catLabel+"_neutralHadronEnergyFraction", binEdges_energyFrac);
    //    addTH1D(dirPrefix+jetType+catLabel+"_electronEnergyFraction", binEdges_energyFrac);
    //    addTH1D(dirPrefix+jetType+catLabel+"_photonEnergyFraction", binEdges_energyFrac);
    //    addTH1D(dirPrefix+jetType+catLabel+"_muonEnergyFraction", binEdges_energyFrac);
    //    addTH1D(dirPrefix+jetType+catLabel+"_chargedHadronMultiplicity", binEdges_dauMult1);
    //    addTH1D(dirPrefix+jetType+catLabel+"_neutralHadronMultiplicity", binEdges_dauMult1);
    //    addTH1D(dirPrefix+jetType+catLabel+"_electronMultiplicity", binEdges_dauMult2);
    //    addTH1D(dirPrefix+jetType+catLabel+"_photonMultiplicity", binEdges_dauMult1);
    //    addTH1D(dirPrefix+jetType+catLabel+"_muonMultiplicity", binEdges_dauMult2);

    for (auto const& matchLabel : matchLabels) {
      addTH2D(dirPrefix + jetType + catLabel + "_pt__vs__" + matchLabel + "_pt", binEdges_pt, binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_pt__vs__" + matchLabel + "_eta", binEdges_pt, binEdges_eta);
      addTH2D(
          dirPrefix + jetType + catLabel + "_pt__vs__" + matchLabel + "_minDeltaR", binEdges_pt, binEdges_minDeltaR);
      addTH2D(dirPrefix + jetType + catLabel + "_pt0__vs__" + matchLabel + "_pt", binEdges_pt, binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_pt0__vs__" + matchLabel + "_eta", binEdges_pt, binEdges_eta);
      addTH2D(
          dirPrefix + jetType + catLabel + "_pt0__vs__" + matchLabel + "_minDeltaR", binEdges_pt, binEdges_minDeltaR);
      addTH2D(
          dirPrefix + jetType + catLabel + "_eta__vs__" + matchLabel + "_minDeltaR", binEdges_eta, binEdges_minDeltaR);

      addTH2D(dirPrefix + jetType + catLabel + "_HT__vs__" + matchLabel + "_HT", binEdges_HT, binEdges_HT);
      addTH2D(dirPrefix + jetType + catLabel + "_MHT__vs__" + matchLabel + "_MHT", binEdges_MHT, binEdges_MHT);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_njets", binEdges_njets);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_HT", binEdges_HT);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_MHT", binEdges_MHT);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt", binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0", binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_eta", binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_eta__vs__pt", binEdges_eta, binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_phi", binEdges_phi);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass", binEdges_mass);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_numberOfDaughters", binEdges_numberOfDaughters);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_chargedHadronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_neutralHadronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_electronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_photonEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_muonEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_chargedHadronMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_neutralHadronMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_electronMultiplicity", binEdges_dauMult2);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_photonMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_MatchedTo"+matchLabel+"_muonMultiplicity", binEdges_dauMult2);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_dRmatch", binEdges_dRmatch);

      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt__vs__" + matchLabel + "_pt",
              binEdges_pt,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0__vs__" + matchLabel + "_pt",
              binEdges_pt,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0__vs__" + matchLabel + "_eta",
              binEdges_pt,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_eta__vs__" + matchLabel + "_eta",
              binEdges_eta,
              binEdges_eta);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel, binEdges_response);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__" +
                  matchLabel + "_eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__nPU",
              binEdges_response,
              binEdges_nPU);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__nCTie4",
              binEdges_response,
              binEdges_nCTie4);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC",
              binEdges_response);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__" +
                  matchLabel + "_eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__nPU",
              binEdges_response,
              binEdges_nPU);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__nCTie4",
              binEdges_response,
              binEdges_nCTie4);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel, binEdges_response);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__" +
                  matchLabel + "_eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__nPU",
              binEdges_response,
              binEdges_nPU);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel + "__vs__nCTie4",
              binEdges_response,
              binEdges_nCTie4);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC",
              binEdges_response);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__" +
                  matchLabel + "_eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__nPU",
              binEdges_response,
              binEdges_nPU);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC__vs__nCTie4",
              binEdges_response,
              binEdges_nCTie4);

      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel,
              binEdges_response);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__" +
                  matchLabel + "_eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__" +
                  matchLabel + "_mass",
              binEdges_response,
              binEdges_mass);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__eta",
              binEdges_response,
              binEdges_eta);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__mass",
              binEdges_response,
              binEdges_mass);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__nPU",
              binEdges_response,
              binEdges_nPU);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel + "__vs__nCTie4",
              binEdges_response,
              binEdges_nCTie4);

      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_njets", binEdges_njets);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_HT", binEdges_HT);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_MHT", binEdges_MHT);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_pt", binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_pt0", binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_eta", binEdges_eta);
      addTH2D(
          dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_eta__vs__pt", binEdges_eta, binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_phi", binEdges_phi);
      addTH1D(dirPrefix + jetType + catLabel + "_NotMatchedTo" + matchLabel + "_mass", binEdges_mass);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_numberOfDaughters", binEdges_numberOfDaughters);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_chargedHadronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_neutralHadronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_electronEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_photonEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_muonEnergyFraction", binEdges_energyFrac);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_chargedHadronMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_neutralHadronMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_electronMultiplicity", binEdges_dauMult2);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_photonMultiplicity", binEdges_dauMult1);
      //      addTH1D(dirPrefix+jetType+catLabel+"_NotMatchedTo"+matchLabel+"_muonMultiplicity", binEdges_dauMult2);
    }
  }
}

void JetMETPerformanceAnalysisDriver::fillHistograms_Jets(const std::string& dir,
                                                          const fillHistoDataJets& fhData,
                                                          float const weight) {
  auto dirPrefix(dir);
  while (dirPrefix.back() == '/') {
    dirPrefix.pop_back();
  }
  if (not dirPrefix.empty()) {
    dirPrefix += "/";
  }

  auto const jetCollRequiresJecA{utils::stringEndsWith(fhData.jetCollection, "CorrA")};
  auto const jetCollWithPtMax{fhData.jetCollection == "L1EmulJet1"};
  auto jetCollBranchName{fhData.jetCollection};
  if (jetCollRequiresJecA) {
    jetCollBranchName = fhData.jetCollection.substr(0, fhData.jetCollection.size() - 5);
  } else if (jetCollWithPtMax) {
    jetCollBranchName = "L1EmulJet";
  }

  if (not hasTTreeReaderValue("n" + jetCollBranchName)) {
    return;
  }

  auto const v_pt_size = this->value<int>("n" + jetCollBranchName);

  std::vector<float> v_pt{};
  std::vector<float> v_eta{};
  std::vector<float> v_phi{};
  std::vector<float> v_mass{};

  v_pt.reserve(v_pt_size);
  v_eta.reserve(v_pt_size);
  v_phi.reserve(v_pt_size);
  v_mass.reserve(v_pt_size);

  auto const& a_pt = this->array<float>(jetCollBranchName + "_pt");
  auto const& a_eta = this->array<float>(jetCollBranchName + "_eta");
  auto const& a_phi = this->array<float>(jetCollBranchName + "_phi");

  auto const a_mass_valid = hasTTreeReaderValue(jetCollBranchName + "_mass");
  auto const* ap_mass = a_mass_valid ? &(this->array<float>(jetCollBranchName + "_mass")) : nullptr;

  for (auto idx = 0; idx < v_pt_size; ++idx) {
    float corr = 1;
    if (jetCollRequiresJecA) {
      corr = jecA_.correction(a_pt[idx], a_eta[idx]);
    }

    v_pt.emplace_back(a_pt[idx] * corr);
    v_eta.emplace_back(a_eta[idx]);
    v_phi.emplace_back(a_phi[idx]);
    v_mass.emplace_back(ap_mass ? (*ap_mass)[idx] * corr : 0);
  }

  //!!  float const* v_pt = nullptr;
  //!!  float const* v_eta = nullptr;
  //!!  float const* v_phi = nullptr;
  //!!  float const* v_mass = nullptr;
  //!!
  //!!  float v_l1t_pt[v_pt_size];
  //!!  float v_l1t_eta[v_pt_size];
  //!!  float v_l1t_phi[v_pt_size];
  //!!
  //!!  if (fhData.jetCollection == "L1EmulJet") {
  //!!
  //!!    auto* const tmpv_iet = this->array_ptr<int>(fhData.jetCollection+"_iet");
  //!!    auto* const tmpv_ieta = this->array_ptr<int>(fhData.jetCollection+"_ieta");
  //!!    auto* const tmpv_iphi = this->array_ptr<int>(fhData.jetCollection+"_iphi");
  //!!
  //!!    for (auto idx = 0; idx < v_pt_size; ++idx) {
  //!!
  //!!      v_l1t_pt[idx] = tmpv_iet[idx] * 0.5f;
  //!!      v_l1t_eta[idx] = tmpv_ieta[idx] * 0.087f;
  //!!
  //!!      float const phi0 = tmpv_iphi[idx] * 0.087f;
  //!!      v_l1t_phi[idx] = phi0 >= M_PI ? phi0 - 2.f * M_PI : phi0;
  //!!    }
  //!!
  //!!    v_pt = v_l1t_pt;
  //!!    v_eta = v_l1t_eta;
  //!!    v_phi = v_l1t_phi;
  //!!  } else {
  //!!  }

  //  auto const* v_numberOfDaughters(this->vector_ptr<uint>(fhData.jetCollection+"_numberOfDaughters"));
  //
  //  auto const* v_chargedHadronMultiplicity(this->vector_ptr<int>(fhData.jetCollection+"_chargedHadronMultiplicity"));
  //  auto const* v_neutralHadronMultiplicity(this->vector_ptr<int>(fhData.jetCollection+"_neutralHadronMultiplicity"));
  //  auto const* v_electronMultiplicity(this->vector_ptr<int>(fhData.jetCollection+"_electronMultiplicity"));
  //  auto const* v_photonMultiplicity(this->vector_ptr<int>(fhData.jetCollection+"_photonMultiplicity"));
  //  auto const* v_muonMultiplicity(this->vector_ptr<int>(fhData.jetCollection+"_muonMultiplicity"));
  //
  //  auto const* v_chargedHadronEnergyFraction(this->vector_ptr<float>(fhData.jetCollection+"_chargedHadronEnergyFraction"));
  //  auto const* v_neutralHadronEnergyFraction(this->vector_ptr<float>(fhData.jetCollection+"_neutralHadronEnergyFraction"));
  //  auto const* v_electronEnergyFraction(this->vector_ptr<float>(fhData.jetCollection+"_electronEnergyFraction"));
  //  auto const* v_photonEnergyFraction(this->vector_ptr<float>(fhData.jetCollection+"_photonEnergyFraction"));
  //  auto const* v_muonEnergyFraction(this->vector_ptr<float>(fhData.jetCollection+"_muonEnergyFraction"));

  auto const nPU = this->value<float>("Pileup_nTrueInt");
  auto const nCT = this->value<int>("nL1EmulCaloTower");

  unsigned int nCTie4{0};
  auto const& ct_ieta = this->array<int>("L1EmulCaloTower_ieta");
  for (auto idx = 0; idx < nCT; ++idx) {
    if (std::abs(ct_ieta[idx]) <= 4) {
      ++nCTie4;
    }
  }

  std::vector<size_t> fhDataIndices{};
  fhDataIndices.reserve(v_pt_size);
  for (auto idx = 0; idx < v_pt_size; ++idx) {
    auto const passesMinPtCut = fhData.jetPtMin < 0 or v_pt[idx] > fhData.jetPtMin;
    auto const passesMaxPtCut = fhData.jetPtMax < 0 or v_pt[idx] < fhData.jetPtMax;
    auto const passesAbsEtaCut = fhData.jetAbsEtaMax < 0 or std::abs(v_eta[idx]) < fhData.jetAbsEtaMax;
    if (passesMinPtCut and passesMaxPtCut and passesAbsEtaCut) {
      fhDataIndices.emplace_back(idx);
    }
  }

  for (auto const& catLabel : jetCategoryLabels_) {
    std::vector<size_t> jetIndices;
    jetIndices.reserve(v_pt_size);
    int indexMaxPtJet(-1);
    float jetPtMax(-1.);
    for (auto idx : fhDataIndices) {
      if (jetBelongsToCategory(catLabel, v_pt[idx], std::abs(v_eta[idx]), nCTie4)) {
        jetIndices.emplace_back(idx);
        if ((jetIndices.size() == 1) or (v_pt[idx] > jetPtMax)) {
          jetPtMax = v_pt[idx];
          indexMaxPtJet = idx;
        }
      }
    }

    float sumPt(0.), sumPx(0.), sumPy(0.);

    for (auto const jetIdx : jetIndices) {
      sumPt += v_pt[jetIdx];
      sumPx += v_pt[jetIdx] * std::cos(v_phi[jetIdx]);
      sumPy += v_pt[jetIdx] * std::sin(v_phi[jetIdx]);

      H1(dirPrefix + fhData.jetCollection + catLabel + "_pt")->Fill(v_pt[jetIdx], weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__nPU")->Fill(v_pt[jetIdx], nPU, weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__nCTie4")->Fill(v_pt[jetIdx], nCTie4, weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_eta")->Fill(v_eta[jetIdx], weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_eta__vs__pt")->Fill(v_eta[jetIdx], v_pt[jetIdx], weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_eta__vs__nPU")->Fill(v_eta[jetIdx], nPU, weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_eta__vs__nCTie4")->Fill(v_eta[jetIdx], nCTie4, weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_phi")->Fill(v_phi[jetIdx], weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_mass")->Fill(v_mass[jetIdx], weight);

      //      if(v_numberOfDaughters          ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_numberOfDaughters"          )->Fill(v_numberOfDaughters          ->at(jetIdx), weight); }
      //      if(v_chargedHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_chargedHadronMultiplicity"  )->Fill(v_chargedHadronMultiplicity  ->at(jetIdx), weight); }
      //      if(v_neutralHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_neutralHadronMultiplicity"  )->Fill(v_neutralHadronMultiplicity  ->at(jetIdx), weight); }
      //      if(v_electronMultiplicity       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_electronMultiplicity"       )->Fill(v_electronMultiplicity       ->at(jetIdx), weight); }
      //      if(v_photonMultiplicity         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_photonMultiplicity"         )->Fill(v_photonMultiplicity         ->at(jetIdx), weight); }
      //      if(v_muonMultiplicity           ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_muonMultiplicity"           )->Fill(v_muonMultiplicity           ->at(jetIdx), weight); }
      //      if(v_chargedHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_chargedHadronEnergyFraction")->Fill(v_chargedHadronEnergyFraction->at(jetIdx), weight); }
      //      if(v_neutralHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_neutralHadronEnergyFraction")->Fill(v_neutralHadronEnergyFraction->at(jetIdx), weight); }
      //      if(v_electronEnergyFraction     ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_electronEnergyFraction"     )->Fill(v_electronEnergyFraction     ->at(jetIdx), weight); }
      //      if(v_photonEnergyFraction       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_photonEnergyFraction"       )->Fill(v_photonEnergyFraction       ->at(jetIdx), weight); }
      //      if(v_muonEnergyFraction         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_muonEnergyFraction"         )->Fill(v_muonEnergyFraction         ->at(jetIdx), weight); }
    }

    H1(dirPrefix + fhData.jetCollection + catLabel + "_njets")->Fill(0.01 + jetIndices.size(), weight);

    H1(dirPrefix + fhData.jetCollection + catLabel + "_HT")->Fill(sumPt, weight);
    H1(dirPrefix + fhData.jetCollection + catLabel + "_MHT")->Fill(std::sqrt(sumPx * sumPx + sumPy * sumPy), weight);

    if (indexMaxPtJet >= 0) {
      H1(dirPrefix + fhData.jetCollection + catLabel + "_pt0")->Fill(v_pt[indexMaxPtJet], weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__nPU")->Fill(v_pt[indexMaxPtJet], nPU, weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__nCTie4")->Fill(v_pt[indexMaxPtJet], nCTie4, weight);
    }
  }

  for (auto const& fhDataMatch : fhData.matches) {
    auto const matchLabel(fhDataMatch.label);
    auto const matchJetColl(fhDataMatch.jetCollection);
    auto const matchJetPtMin(fhDataMatch.jetPtMin);
    auto const matchJetPtMax(fhDataMatch.jetPtMax);
    auto const matchJetDeltaR2Min{fhDataMatch.jetDeltaRMin * fhDataMatch.jetDeltaRMin};

    auto const matchJetCollRequiresJecA{utils::stringEndsWith(matchJetColl, "CorrA")};
    auto const matchJetCollWithPtMax{matchJetColl == "L1EmulJet1"};
    auto matchJetCollBranchName{matchJetColl};
    if (matchJetCollRequiresJecA) {
      matchJetCollBranchName = matchJetColl.substr(0, matchJetColl.size() - 5);
    } else if (matchJetCollWithPtMax) {
      matchJetCollBranchName = "L1EmulJet";
    }

    if (not hasTTreeReaderValue("n" + matchJetCollBranchName)) {
      continue;
    }

    auto const v_match_pt_size = this->value<int>("n" + matchJetCollBranchName);

    std::vector<float> v_match_pt{};
    std::vector<float> v_match_eta{};
    std::vector<float> v_match_phi{};
    std::vector<float> v_match_mass{};

    v_match_pt.reserve(v_match_pt_size);
    v_match_eta.reserve(v_match_pt_size);
    v_match_phi.reserve(v_match_pt_size);
    v_match_mass.reserve(v_match_pt_size);

    auto const& a_match_pt = this->array<float>(matchJetCollBranchName + "_pt");
    auto const& a_match_eta = this->array<float>(matchJetCollBranchName + "_eta");
    auto const& a_match_phi = this->array<float>(matchJetCollBranchName + "_phi");

    auto const a_match_mass_valid = hasTTreeReaderValue(matchJetCollBranchName + "_mass");
    auto const* ap_match_mass = a_match_mass_valid ? &(this->array<float>(matchJetCollBranchName + "_mass")) : nullptr;

    for (auto idx = 0; idx < v_match_pt_size; ++idx) {
      float corr = 1;
      if (matchJetCollRequiresJecA) {
        corr = jecA_.correction(a_match_pt[idx], a_match_eta[idx]);
      }

      v_match_pt.emplace_back(a_match_pt[idx] * corr);
      v_match_eta.emplace_back(a_match_eta[idx]);
      v_match_phi.emplace_back(a_match_phi[idx]);
      v_match_mass.emplace_back(ap_match_mass ? (*ap_match_mass)[idx] * corr : 0);
    }

    std::map<size_t, size_t> mapMatchIndices;
    std::vector<float> vecMatchMinDeltaR2(v_pt_size, -1.f);
    for (auto idx : fhDataIndices) {
      int indexBestMatch = -1;
      auto& dR2min = vecMatchMinDeltaR2[idx];
      for (auto idxMatch = 0; idxMatch < v_match_pt_size; ++idxMatch) {
        auto const passesMatchJetPtMin = matchJetPtMin < 0 or v_match_pt[idxMatch] > matchJetPtMin;
        auto const passesMatchJetPtMax = matchJetPtMax < 0 or v_match_pt[idxMatch] < matchJetPtMax;
        if (not(passesMatchJetPtMin and passesMatchJetPtMax)) {
          continue;
        }

        auto const dR2 = utils::deltaR2(v_eta[idx], v_phi[idx], v_match_eta[idxMatch], v_match_phi[idxMatch]);
        if (dR2min < 0 or dR2 < dR2min) {
          dR2min = dR2;
          if (dR2 < matchJetDeltaR2Min) {
            indexBestMatch = idxMatch;
          }
        }
      }

      if (indexBestMatch >= 0) {
        mapMatchIndices.insert(std::make_pair(idx, indexBestMatch));
      }
    }

    for (auto const& catLabel : jetCategoryLabels_) {
      std::vector<size_t> jetIndices;
      jetIndices.reserve(fhDataIndices.size());
      for (auto idx : fhDataIndices) {
        if (jetBelongsToCategory(catLabel, v_pt[idx], std::abs(v_eta[idx]), nCTie4)) {
          jetIndices.emplace_back(idx);
        }
      }

      // indices of match-jets with same selection as target jets (used for HT and MHT)
      std::vector<size_t> jetMatchRefIndices;
      jetMatchRefIndices.reserve(v_match_pt_size);
      for (auto idx = 0; idx < v_match_pt_size; ++idx) {
        auto const passesMinPtCut = fhData.jetPtMin < 0 or v_match_pt[idx] > fhData.jetPtMin;
        auto const passesMaxPtCut = fhData.jetPtMax < 0 or v_match_pt[idx] < fhData.jetPtMax;
        auto const passesAbsEtaCut = fhData.jetAbsEtaMax < 0 or std::abs(v_match_eta[idx]) < fhData.jetAbsEtaMax;

        if (not(passesMinPtCut and passesMaxPtCut and passesAbsEtaCut)) {
          continue;
        }

        if (jetBelongsToCategory(catLabel, v_match_pt[idx], std::abs(v_match_eta[idx]), nCTie4)) {
          jetMatchRefIndices.emplace_back(idx);
        }
      }

      float sumPt(0.), sumPx(0.), sumPy(0.);
      for (auto const jetIdx : jetIndices) {
        auto const jetPt(v_pt[jetIdx]);
        auto const jetPhi(v_phi[jetIdx]);

        sumPt += jetPt;
        sumPx += jetPt * std::cos(jetPhi);
        sumPy += jetPt * std::sin(jetPhi);
      }

      float sumMatchRefPt(0.), sumMatchRefPx(0.), sumMatchRefPy(0.);
      for (auto const jetMatchRefIdx : jetMatchRefIndices) {
        auto const jetMatchRefPt(v_match_pt[jetMatchRefIdx]);
        auto const jetMatchRefPhi(v_match_phi[jetMatchRefIdx]);

        sumMatchRefPt += jetMatchRefPt;
        sumMatchRefPx += jetMatchRefPt * std::cos(jetMatchRefPhi);
        sumMatchRefPy += jetMatchRefPt * std::sin(jetMatchRefPhi);
      }

      H2(dirPrefix + fhData.jetCollection + catLabel + "_HT__vs__" + matchLabel + "_HT")
          ->Fill(sumPt, sumMatchRefPt, weight);
      H2(dirPrefix + fhData.jetCollection + catLabel + "_MHT__vs__" + matchLabel + "_MHT")
          ->Fill(sqrt(sumPx * sumPx + sumPy * sumPy),
                 sqrt(sumMatchRefPx * sumMatchRefPx + sumMatchRefPy * sumMatchRefPy),
                 weight);

      size_t nJetsMatched(0), nJetsNotMatched(0);
      float sumPtMatched(0.), sumPtNotMatched(0.);
      float sumPxMatched(0.), sumPxNotMatched(0.);
      float sumPyMatched(0.), sumPyNotMatched(0.);
      int indexMaxPtJetWithMatch(-1), indexMaxPtJetWithNoMatch(-1);
      float maxPtJetPtWithMatch(-1.), maxPtJetPtWithNoMatch(-1.);

      int indexCounter(-1);
      for (auto const jetIdx : jetIndices) {
        ++indexCounter;

        auto const jetPt(v_pt[jetIdx]);
        auto const jetEta(v_eta[jetIdx]);
        auto const jetPhi(v_phi[jetIdx]);
        auto const jetMass(v_mass[jetIdx]);

        auto const hasMatch(mapMatchIndices.find(jetIdx) != mapMatchIndices.end());

        auto const minDeltaR = vecMatchMinDeltaR2.at(jetIdx) < 0.f ? -1.f : std::sqrt(vecMatchMinDeltaR2.at(jetIdx));

        if (hasMatch) {
          ++nJetsMatched;

          sumPtMatched += jetPt;
          sumPxMatched += jetPt * std::cos(jetPhi);
          sumPyMatched += jetPt * std::sin(jetPhi);

          if ((nJetsMatched == 1) or (jetPt > maxPtJetPtWithMatch)) {
            maxPtJetPtWithMatch = jetPt;
            indexMaxPtJetWithMatch = jetIdx;
          }

          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt")->Fill(jetPt, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_eta")->Fill(jetEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_eta__vs__pt")
              ->Fill(jetEta, jetPt, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_phi")->Fill(jetPhi, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass")->Fill(jetMass, weight);

          //          if(v_numberOfDaughters          ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_numberOfDaughters"          )->Fill(v_numberOfDaughters->at(jetIdx), weight); }
          //          if(v_chargedHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_chargedHadronMultiplicity"  )->Fill(v_chargedHadronMultiplicity->at(jetIdx), weight); }
          //          if(v_neutralHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_neutralHadronMultiplicity"  )->Fill(v_neutralHadronMultiplicity->at(jetIdx), weight); }
          //          if(v_electronMultiplicity       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_electronMultiplicity"       )->Fill(v_electronMultiplicity->at(jetIdx), weight); }
          //          if(v_photonMultiplicity         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_photonMultiplicity"         )->Fill(v_photonMultiplicity->at(jetIdx), weight); }
          //          if(v_muonMultiplicity           ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_muonMultiplicity"           )->Fill(v_muonMultiplicity->at(jetIdx), weight); }
          //          if(v_chargedHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_chargedHadronEnergyFraction")->Fill(v_chargedHadronEnergyFraction->at(jetIdx), weight); }
          //          if(v_neutralHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_neutralHadronEnergyFraction")->Fill(v_neutralHadronEnergyFraction->at(jetIdx), weight); }
          //          if(v_electronEnergyFraction     ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_electronEnergyFraction"     )->Fill(v_electronEnergyFraction->at(jetIdx), weight); }
          //          if(v_photonEnergyFraction       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_photonEnergyFraction"       )->Fill(v_photonEnergyFraction->at(jetIdx), weight); }
          //          if(v_muonEnergyFraction         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_MatchedTo"+matchLabel+"_muonEnergyFraction"         )->Fill(v_muonEnergyFraction->at(jetIdx), weight); }

          auto const jetMatchIdx(mapMatchIndices.at(jetIdx));

          auto const jetMatchPt(v_match_pt[jetMatchIdx]);
          auto const jetMatchEta(v_match_eta[jetMatchIdx]);
          auto const jetMatchPhi(v_match_phi[jetMatchIdx]);
          auto const jetMatchMass(v_match_mass[jetMatchIdx]);

          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_pt")
              ->Fill(jetPt, jetMatchPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_eta")
              ->Fill(jetPt, jetMatchEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_minDeltaR")
              ->Fill(jetPt, minDeltaR, weight);

          if (indexCounter == 0) {
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_pt")
                ->Fill(jetPt, jetMatchPt, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_eta")
                ->Fill(jetPt, jetMatchEta, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_minDeltaR")
                ->Fill(jetPt, minDeltaR, weight);
          }

          H2(dirPrefix + fhData.jetCollection + catLabel + "_eta__vs__" + matchLabel + "_minDeltaR")
              ->Fill(jetEta, minDeltaR, weight);

          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt__vs__" + matchLabel + "_pt")
              ->Fill(jetPt, jetMatchPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_eta__vs__" + matchLabel +
             "_eta")
              ->Fill(jetEta, jetMatchEta, weight);

          auto const dR2match(utils::deltaR2(jetEta, jetPhi, jetMatchEta, jetMatchPhi));
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_dRmatch")
              ->Fill(sqrt(dR2match), weight);

          auto const jetPtRatio{jetPt / jetMatchPt};
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel)
              ->Fill(jetPtRatio, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__" + matchLabel + "_pt")
              ->Fill(jetPtRatio, jetMatchPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__" + matchLabel + "_eta")
              ->Fill(jetPtRatio, jetMatchEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__pt")
              ->Fill(jetPtRatio, jetPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__eta")
              ->Fill(jetPtRatio, jetEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__nPU")
              ->Fill(jetPtRatio, nPU, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
             "__vs__nCTie4")
              ->Fill(jetPtRatio, nCTie4, weight);

          auto const jetPtRatio2{jetMatchPt / jetPt};
          H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC")
              ->Fill(jetPtRatio2, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__" + matchLabel + "_pt")
              ->Fill(jetPtRatio2, jetMatchPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__" + matchLabel + "_eta")
              ->Fill(jetPtRatio2, jetMatchEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__pt")
              ->Fill(jetPtRatio2, jetPt, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__eta")
              ->Fill(jetPtRatio2, jetEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__nPU")
              ->Fill(jetPtRatio2, nPU, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
             "overREC__vs__nCTie4")
              ->Fill(jetPtRatio2, nCTie4, weight);

          if (jetMatchMass != 0.) {
            auto const jetMassRatio{jetMass / jetMatchMass};
            H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel)
                ->Fill(jetMassRatio, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__" + matchLabel + "_pt")
                ->Fill(jetMassRatio, jetMatchPt, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__" + matchLabel + "_eta")
                ->Fill(jetMassRatio, jetMatchEta, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__" + matchLabel + "_mass")
                ->Fill(jetMassRatio, jetMatchMass, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__pt")
                ->Fill(jetMassRatio, jetPt, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__eta")
                ->Fill(jetMassRatio, jetEta, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__mass")
                ->Fill(jetMassRatio, jetMass, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__nPU")
                ->Fill(jetMassRatio, nPU, weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_mass_over" + matchLabel +
               "__vs__nCTie4")
                ->Fill(jetMassRatio, nCTie4, weight);
          }
        } else {
          ++nJetsNotMatched;

          sumPtNotMatched += jetPt;
          sumPxNotMatched += jetPt * std::cos(jetPhi);
          sumPyNotMatched += jetPt * std::sin(jetPhi);

          if ((nJetsNotMatched == 1) or (jetPt > maxPtJetPtWithNoMatch)) {
            maxPtJetPtWithNoMatch = jetPt;
            indexMaxPtJetWithNoMatch = jetIdx;
          }

          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_pt")->Fill(jetPt, -1., weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_eta")->Fill(jetPt, -99., weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_pt__vs__" + matchLabel + "_minDeltaR")
              ->Fill(jetPt, minDeltaR, weight);

          if (indexCounter == 0) {
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_pt")
                ->Fill(jetPt, -1., weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_eta")
                ->Fill(jetPt, -99., weight);
            H2(dirPrefix + fhData.jetCollection + catLabel + "_pt0__vs__" + matchLabel + "_minDeltaR")
                ->Fill(jetPt, minDeltaR, weight);
          }

          H2(dirPrefix + fhData.jetCollection + catLabel + "_eta__vs__" + matchLabel + "_minDeltaR")
              ->Fill(jetEta, minDeltaR, weight);

          H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_pt")->Fill(jetPt, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_eta")->Fill(jetEta, weight);
          H2(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_eta__vs__pt")
              ->Fill(jetEta, jetPt, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_phi")->Fill(jetPhi, weight);
          H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_mass")
              ->Fill(jetMass, weight);

          //          if(v_numberOfDaughters          ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_numberOfDaughters"          )->Fill(v_numberOfDaughters          ->at(jetIdx), weight); }
          //          if(v_chargedHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_chargedHadronMultiplicity"  )->Fill(v_chargedHadronMultiplicity  ->at(jetIdx), weight); }
          //          if(v_neutralHadronMultiplicity  ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_neutralHadronMultiplicity"  )->Fill(v_neutralHadronMultiplicity  ->at(jetIdx), weight); }
          //          if(v_electronMultiplicity       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_electronMultiplicity"       )->Fill(v_electronMultiplicity       ->at(jetIdx), weight); }
          //          if(v_photonMultiplicity         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_photonMultiplicity"         )->Fill(v_photonMultiplicity         ->at(jetIdx), weight); }
          //          if(v_muonMultiplicity           ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_muonMultiplicity"           )->Fill(v_muonMultiplicity           ->at(jetIdx), weight); }
          //          if(v_chargedHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_chargedHadronEnergyFraction")->Fill(v_chargedHadronEnergyFraction->at(jetIdx), weight); }
          //          if(v_neutralHadronEnergyFraction){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_neutralHadronEnergyFraction")->Fill(v_neutralHadronEnergyFraction->at(jetIdx), weight); }
          //          if(v_electronEnergyFraction     ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_electronEnergyFraction"     )->Fill(v_electronEnergyFraction     ->at(jetIdx), weight); }
          //          if(v_photonEnergyFraction       ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_photonEnergyFraction"       )->Fill(v_photonEnergyFraction       ->at(jetIdx), weight); }
          //          if(v_muonEnergyFraction         ){ H1(dirPrefix+fhData.jetCollection+catLabel+"_NotMatchedTo"+matchLabel+"_muonEnergyFraction"         )->Fill(v_muonEnergyFraction         ->at(jetIdx), weight); }
        }
      }

      H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_njets")
          ->Fill(0.01 + nJetsMatched, weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_njets")
          ->Fill(0.01 + nJetsNotMatched, weight);

      H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_HT")->Fill(sumPtMatched, weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_HT")
          ->Fill(sumPtNotMatched, weight);

      H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_MHT")
          ->Fill(sqrt(sumPxMatched * sumPxMatched + sumPyMatched * sumPyMatched), weight);
      H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_MHT")
          ->Fill(sqrt(sumPxNotMatched * sumPxNotMatched + sumPyNotMatched * sumPyNotMatched), weight);

      if (indexMaxPtJetWithMatch >= 0) {
        auto const maxPtJetPt(v_pt[indexMaxPtJetWithMatch]);
        auto const maxPtJetEta(v_eta[indexMaxPtJetWithMatch]);
        auto const maxPtJetMatchPt(v_match_pt[mapMatchIndices.at(indexMaxPtJetWithMatch)]);
        auto const maxPtJetMatchEta(v_match_eta[mapMatchIndices.at(indexMaxPtJetWithMatch)]);
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0")->Fill(maxPtJetPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0__vs__" + matchLabel + "_pt")
            ->Fill(maxPtJetPt, maxPtJetMatchPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0__vs__" + matchLabel + "_eta")
            ->Fill(maxPtJetPt, maxPtJetMatchEta, weight);

        auto const maxPtJetPtRatio{maxPtJetPt / maxPtJetMatchPt};
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel)
            ->Fill(maxPtJetPtRatio, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__" + matchLabel + "_pt")
            ->Fill(maxPtJetPtRatio, maxPtJetMatchPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__" + matchLabel + "_eta")
            ->Fill(maxPtJetPtRatio, maxPtJetMatchEta, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__pt")
            ->Fill(maxPtJetPtRatio, maxPtJetPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__eta")
            ->Fill(maxPtJetPtRatio, maxPtJetEta, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__nPU")
            ->Fill(maxPtJetPtRatio, nPU, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_over" + matchLabel +
           "__vs__nCTie4")
            ->Fill(maxPtJetPtRatio, nCTie4, weight);

        auto const maxPtJetPtRatio2{maxPtJetMatchPt / maxPtJetPt};
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel + "overREC")
            ->Fill(maxPtJetPtRatio2, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__" + matchLabel + "_pt")
            ->Fill(maxPtJetPtRatio2, maxPtJetMatchPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__" + matchLabel + "_eta")
            ->Fill(maxPtJetPtRatio2, maxPtJetMatchEta, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__pt")
            ->Fill(maxPtJetPtRatio2, maxPtJetPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__eta")
            ->Fill(maxPtJetPtRatio2, maxPtJetEta, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__nPU")
            ->Fill(maxPtJetPtRatio2, nPU, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt0_" + matchLabel +
           "overREC__vs__nCTie4")
            ->Fill(maxPtJetPtRatio2, nCTie4, weight);
      }

      if (indexMaxPtJetWithNoMatch >= 0) {
        auto const maxPtJetPt(v_pt[indexMaxPtJetWithNoMatch]);
        H1(dirPrefix + fhData.jetCollection + catLabel + "_NotMatchedTo" + matchLabel + "_pt0")
            ->Fill(maxPtJetPt, weight);
      }
    }
  }
}

void JetMETPerformanceAnalysisDriver::bookHistograms_MET(const std::string& dir,
                                                         const std::string& metType,
                                                         const std::vector<std::string>& matchLabels) {
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  std::vector<float> binEdges_pt(161);
  //  for(uint idx=0; idx<binEdges_pt.size(); ++idx){ binEdges_pt.at(idx) = idx * 5.; }
  //
  //  std::vector<float> binEdges_phi(41);
  //  for(uint idx=0; idx<binEdges_phi.size(); ++idx){ binEdges_phi.at(idx) = M_PI*(0.05*idx - 1.); }
  //
  //  std::vector<float> binEdges_sumEt(121);
  //  for(uint idx=0; idx<binEdges_sumEt.size(); ++idx){ binEdges_sumEt.at(idx) = idx * 50.; }
  //
  //  const std::vector<float> binEdges_offlineNPV(
  //    {0, 10, 15, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 65, 70, 80, 100, 120, 140}
  //  );
  //
  //  addTH1D(dirPrefix+metType+"_pt", binEdges_pt);
  //  addTH1D(dirPrefix+metType+"_phi", binEdges_phi);
  //  addTH1D(dirPrefix+metType+"_sumEt", binEdges_sumEt);
  //
  //  if(matchLabels.empty()){
  //    return;
  //  }
  //
  //  std::vector<float> binEdges_response(101);
  //  for(uint idx=0; idx<binEdges_response.size(); ++idx){ binEdges_response.at(idx) = 0.05*idx; }
  //
  //  std::vector<float> binEdges_deltaPhi(21);
  //  for(uint idx=0; idx<binEdges_deltaPhi.size(); ++idx){ binEdges_deltaPhi.at(idx) = M_PI*0.05*idx; }
  //
  //  std::vector<float> binEdges_deltaPt(61);
  //  for(uint idx=0; idx<binEdges_deltaPt.size(); ++idx){ binEdges_deltaPt.at(idx) = -240+8.*idx; }
  //
  //  for(auto const& matchLabel : matchLabels){
  //
  //    addTH1D(dirPrefix+metType+"_pt_over"+matchLabel, binEdges_response);
  //    addTH1D(dirPrefix+metType+"_deltaPhi"+matchLabel, binEdges_deltaPhi);
  //    addTH1D(dirPrefix+metType+"_sumEt_over"+matchLabel, binEdges_response);
  //    addTH1D(dirPrefix+metType+"_pt_paraTo"+matchLabel, binEdges_deltaPt);
  //    addTH1D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"Minus"+matchLabel, binEdges_deltaPt);
  //    addTH1D(dirPrefix+metType+"_pt_perpTo"+matchLabel, binEdges_deltaPt);
  //
  //    addTH2D(dirPrefix+metType+"_pt__vs__"+matchLabel+"_pt", binEdges_pt, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_phi__vs__"+matchLabel+"_phi", binEdges_phi, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_sumEt__vs__"+matchLabel+"_sumEt", binEdges_sumEt, binEdges_sumEt);
  //
  //    addTH2D(dirPrefix+metType+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_response, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_response, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_response, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_pt_over"+matchLabel+"__vs__offlineNPV", binEdges_response, binEdges_offlineNPV);
  //
  //    addTH2D(dirPrefix+metType+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_deltaPhi, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_deltaPhi, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_deltaPhi, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_deltaPhi"+matchLabel+"__vs__offlineNPV", binEdges_deltaPhi, binEdges_offlineNPV);
  //
  //    addTH2D(dirPrefix+metType+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_response, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_response, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_response, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_sumEt_over"+matchLabel+"__vs__offlineNPV", binEdges_response, binEdges_offlineNPV);
  //
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_deltaPt, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_deltaPt, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_deltaPt, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"__vs__offlineNPV", binEdges_deltaPt, binEdges_offlineNPV);
  //
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_deltaPt, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_deltaPt, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_deltaPt, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__offlineNPV", binEdges_deltaPt, binEdges_offlineNPV);
  //
  //    addTH2D(dirPrefix+metType+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_pt", binEdges_deltaPt, binEdges_pt);
  //    addTH2D(dirPrefix+metType+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_phi", binEdges_deltaPt, binEdges_phi);
  //    addTH2D(dirPrefix+metType+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_sumEt", binEdges_deltaPt, binEdges_sumEt);
  //    addTH2D(dirPrefix+metType+"_pt_perpTo"+matchLabel+"__vs__offlineNPV", binEdges_deltaPt, binEdges_offlineNPV);
  //  }
  //}
  //
  //void JetMETPerformanceAnalysisDriver::fillHistograms_MET(const std::string& dir, const fillHistoDataMET& fhData, float const weight){
  //
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  auto const* v_pt(this->vector_ptr<float>(fhData.metCollection+"_pt"));
  //  auto const* v_phi(this->vector_ptr<float>(fhData.metCollection+"_phi"));
  //  auto const* v_sumEt(this->vector_ptr<float>(fhData.metCollection+"_sumEt"));
  //
  //  uint offlineNPV(0);
  //  auto const* v_offlinePV_z(this->vector_ptr<float>("offlinePrimaryVertices_z"));
  //  if(v_offlinePV_z){ offlineNPV = v_offlinePV_z->size(); }
  //
  //  if(not (v_pt and v_phi and v_sumEt)){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET(\"" << dir << "\", const fillHistoDataMET&) -- "
  //                << "branches not available (histograms will not be filled): "
  //                << fhData.metCollection+"_pt/phi/sumEt" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  if(not ((v_pt->size() == 1) and (v_phi->size() == 1) and (v_sumEt->size() == 1))){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET(\"" << dir << "\", const fillHistoDataMET&) -- "
  //                << "MET branches have invalid size (histograms will not be filled): "
  //                << fhData.metCollection+"_pt/phi/sumEt" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  auto const metPt(v_pt->at(0));
  //  auto const metPhi(v_phi->at(0));
  //  auto const metSumEt(v_sumEt->at(0));
  //
  //  H1(dirPrefix+fhData.metCollection+"_pt")->Fill(metPt, weight);
  //  H1(dirPrefix+fhData.metCollection+"_phi")->Fill(metPhi, weight);
  //  H1(dirPrefix+fhData.metCollection+"_sumEt")->Fill(metSumEt, weight);
  //
  //  for(auto const& fhDataMatch : fhData.matches){
  //
  //    auto const matchLabel(fhDataMatch.label);
  //    auto const matchMetColl(fhDataMatch.metCollection);
  //
  //    auto const* v_match_pt(this->vector_ptr<float>(matchMetColl+"_pt"));
  //    auto const* v_match_phi(this->vector_ptr<float>(matchMetColl+"_phi"));
  //    auto const* v_match_sumEt(this->vector_ptr<float>(matchMetColl+"_sumEt"));
  //
  //    if(not (v_match_pt and v_match_phi and v_match_sumEt)){
  //      if(verbosity_ >= 0){
  //        std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET(\"" << dir << "\", const fillHistoDataMET&) -- "
  //                  << "branches not available (histograms will not be filled): "
  //                  << matchMetColl+"_pt/phi/sumEt" << std::endl;
  //      }
  //      continue;
  //    }
  //
  //    if(not ((v_match_pt->size() == 1) and (v_match_phi->size() == 1) and (v_match_sumEt->size() == 1))){
  //      if(verbosity_ >= 0){
  //        std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET(\"" << dir << "\", const fillHistoDataMET&) -- "
  //                  << "MET branches have invalid size (histograms will not be filled): "
  //                  << matchMetColl+"_pt/phi/sumEt" << std::endl;
  //      }
  //      continue;
  //    }
  //
  //    auto const metMatchPt(v_match_pt->at(0));
  //    auto const metMatchPhi(v_match_phi->at(0));
  //    auto const metMatchSumEt(v_match_sumEt->at(0));
  //
  //    if(metMatchPt != 0.){
  //      auto const metPtRatio(metPt / metMatchPt);
  //      H2(dirPrefix+fhData.metCollection+"_pt__vs__"+matchLabel+"_pt")->Fill(metPt, metMatchPt, weight);
  //      H1(dirPrefix+fhData.metCollection+"_pt_over"+matchLabel)->Fill(metPtRatio, weight);
  //      H2(dirPrefix+fhData.metCollection+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metPtRatio, metMatchPt, weight);
  //      H2(dirPrefix+fhData.metCollection+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metPtRatio, metMatchPhi, weight);
  //      H2(dirPrefix+fhData.metCollection+"_pt_over"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metPtRatio, metMatchSumEt, weight);
  //      H2(dirPrefix+fhData.metCollection+"_pt_over"+matchLabel+"__vs__offlineNPV")->Fill(metPtRatio, offlineNPV, weight);
  //    }
  //
  //    if(metMatchSumEt != 0.){
  //      auto const metSumEtRatio(metSumEt / metMatchSumEt);
  //      H2(dirPrefix+fhData.metCollection+"_sumEt__vs__"+matchLabel+"_sumEt")->Fill(metSumEt, metMatchSumEt, weight);
  //      H1(dirPrefix+fhData.metCollection+"_sumEt_over"+matchLabel)->Fill(metSumEtRatio, weight);
  //      H2(dirPrefix+fhData.metCollection+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metSumEtRatio, metMatchPt, weight);
  //      H2(dirPrefix+fhData.metCollection+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metSumEtRatio, metMatchPhi, weight);
  //      H2(dirPrefix+fhData.metCollection+"_sumEt_over"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metSumEtRatio, metMatchSumEt, weight);
  //      H2(dirPrefix+fhData.metCollection+"_sumEt_over"+matchLabel+"__vs__offlineNPV")->Fill(metSumEtRatio, offlineNPV, weight);
  //    }
  //
  //    auto const metDeltaPhiMatch(utils::deltaPhi(metPhi, metMatchPhi));
  //    H2(dirPrefix+fhData.metCollection+"_phi__vs__"+matchLabel+"_phi")->Fill(metPhi, metMatchPhi, weight);
  //    H1(dirPrefix+fhData.metCollection+"_deltaPhi"+matchLabel)->Fill(metDeltaPhiMatch, weight);
  //    H2(dirPrefix+fhData.metCollection+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metDeltaPhiMatch, metMatchPt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metDeltaPhiMatch, metMatchPhi, weight);
  //    H2(dirPrefix+fhData.metCollection+"_deltaPhi"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metDeltaPhiMatch, metMatchSumEt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_deltaPhi"+matchLabel+"__vs__offlineNPV")->Fill(metDeltaPhiMatch, offlineNPV, weight);
  //
  //    auto const metParaToMatch(metPt*(std::cos(metPhi)*std::cos(metMatchPhi) + std::sin(metPhi)*std::sin(metMatchPhi)));
  //    H1(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel)->Fill(metParaToMatch, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metParaToMatch, metMatchPt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metParaToMatch, metMatchPhi, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metParaToMatch, metMatchSumEt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"__vs__offlineNPV")->Fill(metParaToMatch, offlineNPV, weight);
  //
  //    auto const metParaToMatchMinusMatch(metParaToMatch - metMatchPt);
  //    H1(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"Minus"+matchLabel)->Fill(metParaToMatchMinusMatch, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metParaToMatchMinusMatch, metMatchPt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metParaToMatchMinusMatch, metMatchPhi, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metParaToMatchMinusMatch, metMatchSumEt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_paraTo"+matchLabel+"Minus"+matchLabel+"__vs__offlineNPV")->Fill(metParaToMatchMinusMatch, offlineNPV, weight);
  //
  //    auto const metPerpToMatch(metPt*(std::cos(metPhi)*std::sin(metMatchPhi) - std::sin(metPhi)*std::cos(metMatchPhi)));
  //    H1(dirPrefix+fhData.metCollection+"_pt_perpTo"+matchLabel)->Fill(metPerpToMatch, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_pt")->Fill(metPerpToMatch, metMatchPt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_phi")->Fill(metPerpToMatch, metMatchPhi, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_perpTo"+matchLabel+"__vs__"+matchLabel+"_sumEt")->Fill(metPerpToMatch, metMatchSumEt, weight);
  //    H2(dirPrefix+fhData.metCollection+"_pt_perpTo"+matchLabel+"__vs__offlineNPV")->Fill(metPerpToMatch, offlineNPV, weight);
  //  }
}

void JetMETPerformanceAnalysisDriver::bookHistograms_Jets_2DMaps(const std::string& dir,
                                                                 const std::string& jetType1,
                                                                 const std::string& jetType2) {
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  std::vector<float> binEdges_HT(221);
  //  for(uint idx=0; idx<binEdges_HT.size(); ++idx){ binEdges_HT.at(idx) = idx * 10.; }
  //
  //  addTH2D(dirPrefix+jetType1+"_HT__vs__"+jetType2+"_HT", binEdges_HT, binEdges_HT);
}

void JetMETPerformanceAnalysisDriver::fillHistograms_Jets_2DMaps(const std::string& dir,
                                                                 const fillHistoDataJets& fhData1,
                                                                 const fillHistoDataJets& fhData2,
                                                                 float const weight) {
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  auto const* v_pt1(this->vector_ptr<float>(fhData1.jetCollection+"_pt"));
  //  auto const* v_eta1(this->vector_ptr<float>(fhData1.jetCollection+"_eta"));
  //
  //  if(not (v_pt1 and v_eta1)){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_Jets_2DMaps(\"" << dir << "\", const fillHistoDataJets&, const fillHistoDataJets&) -- "
  //                << "branches not available (histograms will not be filled): "
  //                << fhData1.jetCollection+"_pt/eta" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  auto const* v_pt2(this->vector_ptr<float>(fhData2.jetCollection+"_pt"));
  //  auto const* v_eta2(this->vector_ptr<float>(fhData2.jetCollection+"_eta"));
  //
  //  if(not (v_pt2 and v_eta2)){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_Jets_2DMaps(\"" << dir << "\", const fillHistoDataJets&, const fillHistoDataJets&) -- "
  //                << "branches not available (histograms will not be filled): "
  //                << fhData2.jetCollection+"_pt/eta" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  float sumPt1(0.);
  //  for(size_t idx=0; idx<v_pt1->size(); ++idx){
  //    if(v_pt1->at(idx) > fhData1.jetPtMin and std::abs(v_eta1->at(idx)) < fhData1.jetAbsEtaMax){
  //      sumPt1 += v_pt1->at(idx);
  //    }
  //  }
  //
  //  float sumPt2(0.);
  //  for(size_t idx=0; idx<v_pt2->size(); ++idx){
  //    if(v_pt2->at(idx) > fhData2.jetPtMin and std::abs(v_eta2->at(idx)) < fhData2.jetAbsEtaMax){
  //      sumPt2 += v_pt2->at(idx);
  //    }
  //  }
  //
  //  H2(dirPrefix+fhData1.jetCollection+"_HT__vs__"+fhData2.jetCollection+"_HT")->Fill(sumPt1, sumPt2, weight);
}

void JetMETPerformanceAnalysisDriver::bookHistograms_MET_2DMaps(const std::string& dir,
                                                                const std::string& metType1,
                                                                const std::string& metType2,
                                                                bool const book1D) {
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  std::vector<float> binEdges_pt(81);
  //  for(uint idx=0; idx<binEdges_pt.size(); ++idx){ binEdges_pt.at(idx) = idx * 10.; }
  //
  //  std::vector<float> binEdges_phi(41);
  //  for(uint idx=0; idx<binEdges_phi.size(); ++idx){ binEdges_phi.at(idx) = M_PI*(0.05*idx - 1.); }
  //
  //  std::vector<float> binEdges_sumEt(221);
  //  for(uint idx=0; idx<binEdges_sumEt.size(); ++idx){ binEdges_sumEt.at(idx) = idx * 10.; }
  //
  //  if(book1D){
  //    addTH1D(dirPrefix+metType1+"_pt", binEdges_pt);
  //    addTH1D(dirPrefix+metType1+"_phi", binEdges_phi);
  //    addTH1D(dirPrefix+metType1+"_sumEt", binEdges_sumEt);
  //
  //    addTH1D(dirPrefix+metType2+"_pt", binEdges_pt);
  //    addTH1D(dirPrefix+metType2+"_phi", binEdges_phi);
  //    addTH1D(dirPrefix+metType2+"_sumEt", binEdges_sumEt);
  //  }
  //
  //  addTH2D(dirPrefix+metType1+"_pt__vs__"+metType2+"_pt", binEdges_pt, binEdges_pt);
  //  addTH2D(dirPrefix+metType1+"_phi__vs__"+metType2+"_phi", binEdges_phi, binEdges_phi);
  //  addTH2D(dirPrefix+metType1+"_sumEt__vs__"+metType2+"_sumEt", binEdges_sumEt, binEdges_sumEt);
}

void JetMETPerformanceAnalysisDriver::fillHistograms_MET_2DMaps(const std::string& dir,
                                                                const fillHistoDataMET& fhData1,
                                                                const fillHistoDataMET& fhData2,
                                                                bool const fill1D,
                                                                float const weight) {
  //  auto dirPrefix(dir);
  //  while (dirPrefix.back() == '/') { dirPrefix.pop_back(); }
  //  if(not dirPrefix.empty()){ dirPrefix += "/"; }
  //
  //  auto const* v_pt1(this->vector_ptr<float>(fhData1.metCollection+"_pt"));
  //  if(not v_pt1){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET_2DMaps(\"" << dir << "\", const fillHistoDataMET&, const fillHistoDataMET&) -- "
  //                << "branches not available (histograms will not be filled): "
  //                << fhData1.metCollection+"_pt" << std::endl;
  //    }
  //    return;
  //  }
  //  else if(v_pt1->size() != 1){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET_2DMaps(\"" << dir << "\", const fillHistoDataMET&, const fillHistoDataMET&) -- "
  //                << "MET branches have invalid size (histograms will not be filled): "
  //                << fhData1.metCollection+"_pt" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  auto const* v_pt2(this->vector_ptr<float>(fhData2.metCollection+"_pt"));
  //  if(not v_pt2){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET_2DMaps(\"" << dir << "\", const fillHistoDataMET&, const fillHistoDataMET&) -- "
  //                << "branches not available (histograms will not be filled): "
  //                << fhData2.metCollection+"_pt" << std::endl;
  //    }
  //    return;
  //  }
  //  else if(v_pt2->size() != 1){
  //    if(verbosity_ >= 0){
  //      std::cout << "JetMETPerformanceAnalysisDriver::fillHistograms_MET_2DMaps(\"" << dir << "\", const fillHistoDataMET&, const fillHistoDataMET&) -- "
  //                << "MET branches have invalid size (histograms will not be filled): "
  //                << fhData2.metCollection+"_pt" << std::endl;
  //    }
  //    return;
  //  }
  //
  //  auto const* v_phi1(this->vector_ptr<float>(fhData1.metCollection+"_phi"));
  //  auto const* v_phi2(this->vector_ptr<float>(fhData2.metCollection+"_phi"));
  //
  //  auto const* v_sumEt1(this->vector_ptr<float>(fhData1.metCollection+"_sumEt"));
  //  auto const* v_sumEt2(this->vector_ptr<float>(fhData2.metCollection+"_sumEt"));
  //
  //  auto const met1_pt(v_pt1->at(0)), met1_phi(v_phi1->at(0)), met1_sumEt(v_sumEt1->at(0));
  //  auto const met2_pt(v_pt2->at(0)), met2_phi(v_phi2->at(0)), met2_sumEt(v_sumEt2->at(0));
  //
  //  if(fill1D){
  //    H1(dirPrefix+fhData1.metCollection+"_pt")->Fill(met1_pt, weight);
  //    H1(dirPrefix+fhData1.metCollection+"_phi")->Fill(met1_phi, weight);
  //    H1(dirPrefix+fhData1.metCollection+"_sumEt")->Fill(met1_sumEt, weight);
  //
  //    H1(dirPrefix+fhData2.metCollection+"_pt")->Fill(met2_pt, weight);
  //    H1(dirPrefix+fhData2.metCollection+"_phi")->Fill(met2_phi, weight);
  //    H1(dirPrefix+fhData2.metCollection+"_sumEt")->Fill(met2_sumEt, weight);
  //  }
  //
  //  H2(dirPrefix+fhData1.metCollection+"_pt__vs__"+fhData2.metCollection+"_pt")->Fill(met1_pt, met2_pt, weight);
  //  H2(dirPrefix+fhData1.metCollection+"_phi__vs__"+fhData2.metCollection+"_phi")->Fill(met1_phi, met2_phi, weight);
  //  H2(dirPrefix+fhData1.metCollection+"_sumEt__vs__"+fhData2.metCollection+"_sumEt")->Fill(met1_sumEt, met2_sumEt, weight);
}
