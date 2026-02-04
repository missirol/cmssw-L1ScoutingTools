#include <algorithm>
#include <cassert>
#include <cmath>
#include <iomanip>
#include <ostream>

#include "L1ScoutingTools/NTupleAnalysis/interface/JetResponseAnalysisDriver.h"
#include "L1ScoutingTools/NTupleAnalysis/interface/Utils.h"

void JetResponseAnalysisDriver::init() {
  jecA_.init(getOption("jecA_filePath"));

  auto f_to_str = [](float a) -> std::string {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(1) << a;
    auto ret = oss.str();
    std::replace(ret.begin(), ret.end(), '.', 'p');
    return ret;
  };

  auto u_to_str = [](unsigned int b) -> std::string {
    std::ostringstream oss;
    oss << std::setw(3) << std::setfill('0') << b;
    auto ret = oss.str();
    return ret;
  };

  std::vector<float> const absEta_v = {0.0f, 0.2f, 0.4f, 0.6f, 0.8f, 1.0f, 1.3f, 1.6f, 1.9f, 2.2f, 2.5f};

  for (auto ai = 0u; (ai + 1) < absEta_v.size(); ++ai) {
    auto const a0 = absEta_v[ai];
    auto const a1 = absEta_v[ai + 1];

    std::vector<unsigned int> nCTie4_v{};
    if (a0 < 0.4f) {
      nCTie4_v = {0, 20, 30, 40, 60, 80};
    } else if (a0 == 1.6f) {
      nCTie4_v = {0, 10, 20, 30, 40, 60};
    } else if (a0 == 1.9f) {
      nCTie4_v = {0, 10, 20, 30, 40, 60};
    } else if (a0 == 2.2f) {
      nCTie4_v = {0, 10};
    } else {
      nCTie4_v = {0, 10, 20, 30, 40, 60, 80};
    }

    for (auto bi = 0u; bi < nCTie4_v.size(); ++bi) {
      auto const b0 = nCTie4_v[bi];

      std::string key{"_absEta"};
      key += f_to_str(a0);
      assert(key.size() == 10);

      key += "to" + f_to_str(a1);
      assert(key.size() == 15);

      key += "nCTie4" + u_to_str(b0) + "to";
      assert(key.size() == 26);

      if ((bi + 1) == nCTie4_v.size()) {
        key += "Inf";
        jetCategoryForJECFuncMap_[key] = [a0, a1, b0](float a, unsigned int b) {
          return (a0 <= a and a < a1 and b0 <= b);
        };
      } else {
        auto const b1 = nCTie4_v[bi + 1];
        key += u_to_str(b1);
        jetCategoryForJECFuncMap_[key] = [a0, a1, b0, b1](float a, unsigned int b) {
          return (a0 <= a and a < a1 and b0 <= b and b < b1);
        };
      }

      assert(key.size() == 29);
    }
  }

  // histogram: events counter
  addTH1D("eventsProcessed", {0, 1});
  addTH1D("weight", 100, -5, 5);
  addTH1D("nPU", 40, 0, 120);
  addTH1D("nCT", 100, 0, 1000);
  addTH1D("nCTie4", 48, 0, 240);
  addTH2D("nPU__vs__nCT", 40, 0, 120, 100, 0, 1000);
  addTH2D("nPU__vs__nCTie4", 40, 0, 120, 48, 0, 240);

  labelMap_jetAK4_ = {
      {"L1EmulJet", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulJet1", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulAK4CTJet0", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulAK4CTJet0Corr", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulAK4CTJet0CorrA", {{"GEN", "GenJetNoMu"}}},
      {"L1EmulAK4CTJet1", {{"GEN", "GenJetNoMu"}}},
  };

  for (auto const& selLabel : {"NoSelection"}) {
    // histograms: AK4 Jets
    for (auto const& jetLabel : labelMap_jetAK4_) {
      bookHistograms_Jets(selLabel, jetLabel.first, utils::mapKeys(jetLabel.second));
    }
  }
}

std::vector<std::string> JetResponseAnalysisDriver::jetCategoryLabelsForJECHistos(
    const std::string& jetColl, const std::string& matchJetLabel) const {
  std::vector<std::string> ret;
  ret.reserve(jetCategoryForJECFuncMap_.size());
  for (auto const& [key, foo] : jetCategoryForJECFuncMap_) {
    ret.emplace_back(key);
  }

  return ret;
}

void JetResponseAnalysisDriver::analyze() {
  //  auto const run = this->value<unsigned int>("run");
  //  auto const luminosityBlock = this->value<unsigned int>("luminosityBlock");
  //  auto const event = this->value<unsigned long long>("event");
  //  std::cout << run << ":" << luminosityBlock << ":" << event << std::endl;

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

  // AK4 Jets
  float const minAK4JetPt{1};
  float const minAK4JetPtRef{7.5f};
  float const maxAK4JetDeltaRmatchRef{0.2};

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
  }
}

void JetResponseAnalysisDriver::bookHistograms_Jets(const std::string& dir,
                                                    const std::string& jetType,
                                                    const std::vector<std::string>& matchLabels) {
  auto dirPrefix(dir);
  while (dirPrefix.back() == '/') {
    dirPrefix.pop_back();
  }
  if (not dirPrefix.empty()) {
    dirPrefix += "/";
  }

  std::vector<float> binEdges_pt(104);
  for (uint idx = 0; idx < binEdges_pt.size(); ++idx) {
    binEdges_pt.at(idx) = std::max(1.f, 10.f * idx);
  }

  std::vector<float> binEdges_eta(101);
  for (uint idx = 0; idx < binEdges_eta.size(); ++idx) {
    binEdges_eta.at(idx) = -5.0 + 0.1 * idx;
  }

  std::vector<float> binEdges_response(101);
  for (uint idx = 0; idx < binEdges_response.size(); ++idx) {
    binEdges_response.at(idx) = 0.05 * idx;
  }

  std::vector<float> binEdges_nPU(41);
  for (uint idx = 0; idx < binEdges_nPU.size(); ++idx) {
    binEdges_nPU.at(idx) = 3 * idx;
  }

  std::vector<float> binEdges_nCT(101);
  for (uint idx = 0; idx < binEdges_nCT.size(); ++idx) {
    binEdges_nCT.at(idx) = 10 * idx;
  }

  std::vector<float> binEdges_nCTie4(49);
  for (uint idx = 0; idx < binEdges_nCTie4.size(); ++idx) {
    binEdges_nCTie4.at(idx) = 5 * idx;
  }

  for (auto const& matchLabel : matchLabels) {
    auto const jetCategoryLabelsForJECHistos_v = jetCategoryLabelsForJECHistos(jetType, matchLabel);
    for (auto const& catLabel : jetCategoryLabelsForJECHistos_v) {
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel + "__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__pt",
              binEdges_response,
              binEdges_pt);
      addTH2D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel + "overREC__vs__" +
                  matchLabel + "_pt",
              binEdges_response,
              binEdges_pt);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_eta", binEdges_eta);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_nCT", binEdges_nCT);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_nCTie4", binEdges_nCTie4);
      addTH1D(dirPrefix + jetType + catLabel + "_MatchedTo" + matchLabel + "_nPU", binEdges_nPU);
    }
  }
}

void JetResponseAnalysisDriver::fillHistograms_Jets(const std::string& dir,
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

  auto const nPU = this->value<float>("Pileup_nTrueInt");
  auto const nCT = this->value<int>("nL1EmulCaloTower");

  unsigned int nCTie4{0};
  auto const& ct_ieta = this->array<int>("L1EmulCaloTower_ieta");
  for (auto idx = 0; idx < nCT; ++idx) {
    if (std::abs(ct_ieta[idx]) <= 4) {
      ++nCTie4;
    }
  }

  if (not hasTTreeReaderValue("n" + jetCollBranchName)) {
    return;
  }

  auto const v_pt_size = this->value<int>("n" + jetCollBranchName);

  std::vector<float> v_pt{};
  std::vector<float> v_eta{};
  std::vector<float> v_phi{};

  v_pt.reserve(v_pt_size);
  v_eta.reserve(v_pt_size);
  v_phi.reserve(v_pt_size);

  auto const& a_pt = this->array<float>(jetCollBranchName + "_pt");
  auto const& a_eta = this->array<float>(jetCollBranchName + "_eta");
  auto const& a_phi = this->array<float>(jetCollBranchName + "_phi");

  for (auto idx = 0; idx < v_pt_size; ++idx) {
    float corr = 1;
    if (jetCollRequiresJecA) {
      corr = jecA_.correction(a_pt[idx], a_eta[idx]);
    }

    v_pt.emplace_back(a_pt[idx] * corr);
    v_eta.emplace_back(a_eta[idx]);
    v_phi.emplace_back(a_phi[idx]);
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

    v_match_pt.reserve(v_match_pt_size);
    v_match_eta.reserve(v_match_pt_size);
    v_match_phi.reserve(v_match_pt_size);

    auto const& a_match_pt = this->array<float>(matchJetCollBranchName + "_pt");
    auto const& a_match_eta = this->array<float>(matchJetCollBranchName + "_eta");
    auto const& a_match_phi = this->array<float>(matchJetCollBranchName + "_phi");

    for (auto idx = 0; idx < v_match_pt_size; ++idx) {
      float corr{1.f};
      if (matchJetCollRequiresJecA) {
        corr = jecA_.correction(a_match_pt[idx], a_match_eta[idx]);
      }

      v_match_pt.emplace_back(a_match_pt[idx] * corr);
      v_match_eta.emplace_back(a_match_eta[idx]);
      v_match_phi.emplace_back(a_match_phi[idx]);
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

    // JEC-related histos
    auto const jetCategoryLabelsForJECHistos_v = jetCategoryLabelsForJECHistos(fhData.jetCollection, matchLabel);
    for (auto const& catLabel : jetCategoryLabelsForJECHistos_v) {
      std::vector<size_t> jetIndices;
      jetIndices.reserve(fhDataIndices.size());
      for (auto idx : fhDataIndices) {
        if (jetCategoryForJECFuncMap_[catLabel](std::abs(v_eta[idx]), nCTie4)) {
          jetIndices.emplace_back(idx);
        }
      }

      for (auto const jetIdx : jetIndices) {
        auto mapMatchIndicesIter(mapMatchIndices.find(jetIdx));
        if (mapMatchIndicesIter == mapMatchIndices.end()) {
          continue;
        }

        auto const jetMatchIdx(mapMatchIndicesIter->second);
        auto const jetMatchPt(v_match_pt.at(jetMatchIdx));

        auto const jetPt(v_pt[jetIdx]);
        auto const jetEta(v_eta[jetIdx]);

        auto const jetPtRatio(jetPt / jetMatchPt);
        auto const jetPtRatio2(jetMatchPt / jetPt);

        if (std::isnan(jetPtRatio)) {
          std::cout << "ERROR: ratio jetPt/jetMatchPt is NaN (jetPt=" << jetPt << ", jetMatchPt=" << jetMatchPt << ")"
                    << " [jetCollection=\"" << fhData.jetCollection << "\", matchJetCollection=\"" << matchJetColl
                    << "\"]" << std::endl;
          assert(false);
        }

        if (std::isnan(jetPtRatio2)) {
          std::cout << "ERROR: ratio jetMatchPt/jetPt is NaN (jetPt=" << jetPt << ", jetMatchPt=" << jetMatchPt << ")"
                    << " [jetCollection=\"" << fhData.jetCollection << "\", matchJetCollection=\"" << matchJetColl
                    << "\"]" << std::endl;
          assert(false);
        }

        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
           "__vs__pt")
            ->Fill(jetPtRatio, jetPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_over" + matchLabel +
           "__vs__" + matchLabel + "_pt")
            ->Fill(jetPtRatio, jetMatchPt, weight);

        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
           "overREC__vs__pt")
            ->Fill(jetPtRatio2, jetPt, weight);
        H2(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_pt_" + matchLabel +
           "overREC__vs__" + matchLabel + "_pt")
            ->Fill(jetPtRatio2, jetMatchPt, weight);

        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_eta")->Fill(jetEta, weight);
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_nCT")->Fill(nCT, weight);
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_nCTie4")->Fill(nCTie4, weight);
        H1(dirPrefix + fhData.jetCollection + catLabel + "_MatchedTo" + matchLabel + "_nPU")->Fill(nPU, weight);
      }
    }
  }
}
