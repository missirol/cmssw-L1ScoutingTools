#include <algorithm>
#include <cassert>
#include <cmath>

#include "L1ScoutingTools/NTupleAnalysis/interface/L1ScoutSelDiJetAnalysisDriver.h"
#include "L1ScoutingTools/NTupleAnalysis/interface/Utils.h"

L1ScoutSelDiJetAnalysisDriver::L1ScoutSelDiJetAnalysisDriver(const std::string& tfile,
                                                             const std::string& ttree,
                                                             const std::string& outputFilePath,
                                                             const std::string& outputFileMode)
    : L1ScoutSelDiJetAnalysisDriver(outputFilePath, outputFileMode) {
  setInputTTree(tfile, ttree);
}

L1ScoutSelDiJetAnalysisDriver::L1ScoutSelDiJetAnalysisDriver(const std::string& outputFilePath,
                                                             const std::string& outputFileMode)
    : AnalysisDriverBase(outputFilePath, outputFileMode) {}

void L1ScoutSelDiJetAnalysisDriver::init() {
  addTH1D("weight", 100, -5, 5);
  addTH1D("eventsProcessed_unwgt", {0, 1});
  addTH1D("eventsProcessed", {0, 1});

  std::vector<float> binEdges_njets(121);
  for (uint idx = 0; idx < binEdges_njets.size(); ++idx) {
    binEdges_njets.at(idx) = idx;
  }

  std::vector<float> binEdges_pt(121);
  for (uint idx = 0; idx < binEdges_pt.size(); ++idx) {
    if (idx == 0) {
      binEdges_pt[idx] = 1.f;
    } else if (idx < 31) {
      binEdges_pt[idx] = idx * 5.f;
    } else if (idx < 51) {
      binEdges_pt[idx] = 150.f + (idx - 30) * 10.f;
    } else if (idx < 81) {
      binEdges_pt[idx] = 350.f + (idx - 50) * 20.f;
    } else if (idx < 96) {
      binEdges_pt[idx] = 950.f + (idx - 80) * 30.f;
    } else if (idx < 108) {
      binEdges_pt[idx] = 1400.f + (idx - 95) * 50.f;
    } else {
      binEdges_pt[idx] = 2000.f + (idx - 107) * 100.f;
    }
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

  std::vector<float> binEdges_mass2(301);
  for (uint idx = 0; idx < binEdges_mass2.size(); ++idx) {
    binEdges_mass2.at(idx) = 2 * idx;
  }

  std::vector<float> binEdges_deltaY(161);
  for (uint idx = 0; idx < binEdges_deltaY.size(); ++idx) {
    binEdges_deltaY.at(idx) = -8.0 + 0.1 * idx;
  }

  std::vector<float> binEdges_deltaEta(161);
  for (uint idx = 0; idx < binEdges_deltaEta.size(); ++idx) {
    binEdges_deltaEta.at(idx) = -8.0 + 0.1 * idx;
  }

  std::vector<float> binEdges_deltaPhi(41);
  for (uint idx = 0; idx < binEdges_deltaPhi.size(); ++idx) {
    binEdges_deltaPhi.at(idx) = M_PI * (0.05 * idx - 1.);
  }

  // L1T Jets
  addTH1D("L1TJet_passSelBx", {0, 1});
  addTH1D("L1TJet_passSelBx_passDiJet30", {0, 1});

  addTH1D("L1TJet_nJets30", binEdges_njets);
  addTH1D("L1TJet_nJets40", binEdges_njets);
  addTH1D("L1TJet_nJets50", binEdges_njets);

  addTH1D("L1TJet_J1_pt", binEdges_pt);
  addTH1D("L1TJet_J1_eta", binEdges_eta);
  addTH2D("L1TJet_J1_eta_phi", binEdges_eta, binEdges_phi);
  addTH1D("L1TJet_J1_phi", binEdges_phi);

  addTH1D("L1TJet_J2_pt", binEdges_pt);
  addTH1D("L1TJet_J2_eta", binEdges_eta);
  addTH2D("L1TJet_J2_eta_phi", binEdges_eta, binEdges_phi);
  addTH1D("L1TJet_J2_phi", binEdges_phi);

  addTH1D("L1TJet_J1J2_pt", binEdges_pt);
  addTH1D("L1TJet_J1J2_eta", binEdges_eta);
  addTH1D("L1TJet_J1J2_phi", binEdges_phi);
  addTH1D("L1TJet_J1J2_mass", binEdges_mass2);
  addTH1D("L1TJet_J1J2_deltaY", binEdges_deltaY);
  addTH1D("L1TJet_J1J2_deltaEta", binEdges_deltaEta);
  addTH1D("L1TJet_J1J2_deltaPhi", binEdges_deltaPhi);

  // L1S AK4CaloJets
  std::vector<float> binEdges_energyCorr(101);
  for (uint idx = 0; idx < binEdges_energyCorr.size(); ++idx) {
    binEdges_energyCorr.at(idx) = 0.05 * idx;
  }

  std::vector<float> binEdges_nConst(61);
  for (uint idx = 0; idx < binEdges_nConst.size(); ++idx) {
    binEdges_nConst.at(idx) = idx;
  }

  addTH1D("L1SAK4CaloJet_passSelBx", {0, 1});
  addTH1D("L1SAK4CaloJet_passSelBx_passDiJet30", {0, 1});

  addTH1D("L1SAK4CaloJet_nJets30", binEdges_njets);
  addTH1D("L1SAK4CaloJet_nJets40", binEdges_njets);
  addTH1D("L1SAK4CaloJet_nJets50", binEdges_njets);

  addTH1D("L1SAK4CaloJet_J1_pt", binEdges_pt);
  addTH1D("L1SAK4CaloJet_J1_eta", binEdges_eta);
  addTH2D("L1SAK4CaloJet_J1_eta_phi", binEdges_eta, binEdges_phi);
  addTH1D("L1SAK4CaloJet_J1_phi", binEdges_phi);
  addTH1D("L1SAK4CaloJet_J1_mass", binEdges_mass);
  addTH1D("L1SAK4CaloJet_J1_energyCorr", binEdges_energyCorr);
  addTH1D("L1SAK4CaloJet_J1_nConst", binEdges_nConst);

  addTH1D("L1SAK4CaloJet_J2_pt", binEdges_pt);
  addTH1D("L1SAK4CaloJet_J2_eta", binEdges_eta);
  addTH2D("L1SAK4CaloJet_J2_eta_phi", binEdges_eta, binEdges_phi);
  addTH1D("L1SAK4CaloJet_J2_phi", binEdges_phi);
  addTH1D("L1SAK4CaloJet_J2_mass", binEdges_mass);
  addTH1D("L1SAK4CaloJet_J2_energyCorr", binEdges_energyCorr);
  addTH1D("L1SAK4CaloJet_J2_nConst", binEdges_nConst);

  addTH1D("L1SAK4CaloJet_J1J2_pt", binEdges_pt);
  addTH1D("L1SAK4CaloJet_J1J2_eta", binEdges_eta);
  addTH1D("L1SAK4CaloJet_J1J2_phi", binEdges_phi);
  addTH1D("L1SAK4CaloJet_J1J2_mass", binEdges_mass2);
  addTH1D("L1SAK4CaloJet_J1J2_deltaY", binEdges_deltaY);
  addTH1D("L1SAK4CaloJet_J1J2_deltaEta", binEdges_deltaEta);
  addTH1D("L1SAK4CaloJet_J1J2_deltaPhi", binEdges_deltaPhi);
}

void L1ScoutSelDiJetAnalysisDriver::analyze() {
  float const wgt{1.f};
  H1("weight")->Fill(wgt);
  H1("eventsProcessed_unwgt")->Fill(0.5);
  H1("eventsProcessed")->Fill(0.5, wgt);

  auto const selBx_DijetEt30 = this->value<bool>("SelBx_DijetEt30");
  auto const selBx_l1ScBXsWithCaloTowers = this->value<bool>("SelBx_l1ScBXsWithCaloTowers");
  if (not(selBx_DijetEt30 and selBx_l1ScBXsWithCaloTowers)) {
    return;
  }

  // L1T Jets
  {
    auto const a_size = this->value<int>("nL1Jet");
    auto const& a_pt = this->array<float>("L1Jet_pt");
    auto const& a_eta = this->array<float>("L1Jet_eta");
    auto const& a_phi = this->array<float>("L1Jet_phi");

    std::vector<size_t> sortIdxs(a_size);
    std::iota(sortIdxs.begin(), sortIdxs.end(), 0);
    std::sort(sortIdxs.begin(), sortIdxs.end(), [&](size_t const i1, size_t const i2) { return a_pt[i1] > a_pt[i2]; });

    Jet j1{};
    Jet j2{};

    unsigned int nJets30{0};
    unsigned int nJets40{0};
    unsigned int nJets50{0};

    for (auto idx : sortIdxs) {
      auto const j_pt{a_pt[idx]};
      auto const j_eta{a_eta[idx]};
      auto const j_absEta{std::abs(j_eta)};

      if (not(j_pt > 30 and j_absEta < 2.5)) {
        continue;
      }

      ++nJets30;

      if (j_pt > 40 and j_absEta < 2.5) {
        ++nJets40;
      }

      if (j_pt > 50 and j_absEta < 2.5) {
        ++nJets50;
      }

      if (nJets30 == 1) {
        j1.p4 = P4f(j_pt, j_eta, a_phi[idx], 0);
      } else if (nJets30 == 2) {
        j2.p4 = P4f(j_pt, j_eta, a_phi[idx], 0);
      }
    }

    H1("L1TJet_passSelBx")->Fill(0.5, wgt);

    if (nJets30 >= 2) {
      H1("L1TJet_passSelBx_passDiJet30")->Fill(0.5, wgt);

      H1("L1TJet_nJets30")->Fill(nJets30, wgt);
      H1("L1TJet_nJets40")->Fill(nJets40, wgt);
      H1("L1TJet_nJets50")->Fill(nJets50, wgt);

      H1("L1TJet_J1_pt")->Fill(j1.p4.pt(), wgt);
      H1("L1TJet_J1_eta")->Fill(j1.p4.eta(), wgt);
      H2("L1TJet_J1_eta_phi")->Fill(j1.p4.eta(), j1.p4.phi(), wgt);
      H1("L1TJet_J1_phi")->Fill(j1.p4.phi(), wgt);

      H1("L1TJet_J2_pt")->Fill(j2.p4.pt(), wgt);
      H1("L1TJet_J2_eta")->Fill(j2.p4.eta(), wgt);
      H2("L1TJet_J2_eta_phi")->Fill(j2.p4.eta(), j2.p4.phi(), wgt);
      H1("L1TJet_J2_phi")->Fill(j2.p4.phi(), wgt);

      auto const j1j2_p4{j1.p4 + j2.p4};

      H1("L1TJet_J1J2_pt")->Fill(j1j2_p4.pt(), wgt);
      H1("L1TJet_J1J2_eta")->Fill(j1j2_p4.eta(), wgt);
      H1("L1TJet_J1J2_phi")->Fill(j1j2_p4.phi(), wgt);
      H1("L1TJet_J1J2_mass")->Fill(j1j2_p4.mass(), wgt);

      H1("L1TJet_J1J2_deltaY")->Fill(j1.p4.Rapidity() - j2.p4.Rapidity(), wgt);
      H1("L1TJet_J1J2_deltaEta")->Fill(j1.p4.eta() - j2.p4.eta(), wgt);
      H1("L1TJet_J1J2_deltaPhi")->Fill(utils::deltaPhi(j1.p4.phi(), j2.p4.phi()), wgt);
    }
  }

  // L1S AK4CaloJets
  {
    auto const a_size = this->value<int>("nL1CaloJet");
    auto const& a_pt = this->array<float>("L1CaloJet_pt");
    auto const& a_eta = this->array<float>("L1CaloJet_eta");
    auto const& a_phi = this->array<float>("L1CaloJet_phi");
    auto const& a_mass = this->array<float>("L1CaloJet_mass");
    auto const& a_energyCorr = this->array<float>("L1CaloJet_energyCorr");
    auto const& a_nConst = this->array<int>("L1CaloJet_nConst");

    std::vector<size_t> sortIdxs(a_size);
    std::iota(sortIdxs.begin(), sortIdxs.end(), 0);
    std::sort(sortIdxs.begin(), sortIdxs.end(), [&](size_t const i1, size_t const i2) { return a_pt[i1] > a_pt[i2]; });

    Jet j1{};
    Jet j2{};

    unsigned int nJets30{0};
    unsigned int nJets40{0};
    unsigned int nJets50{0};

    for (auto idx : sortIdxs) {
      auto const j_pt{a_pt[idx]};
      auto const j_eta{a_eta[idx]};
      auto const j_absEta{std::abs(j_eta)};

      if (not(j_pt > 30 and j_absEta < 2.5)) {
        continue;
      }

      auto const j_nConst{a_nConst[idx]};
      if (j_nConst < 2) {
        continue;
      }

      auto const j_energyCorr{a_energyCorr[idx]};
      // Skip L1S CaloJets with uncorrected-pT above 300 GeV,
      // because JECs are not valid in that phase space
      if (j_pt > (300.f * j_energyCorr)) {
        continue;
      }

      ++nJets30;

      if (j_pt > 40 and j_absEta < 2.5) {
        ++nJets40;
      }

      if (j_pt > 50 and j_absEta < 2.5) {
        ++nJets50;
      }

      if (nJets30 == 1) {
        j1.p4 = P4f(j_pt, j_eta, a_phi[idx], a_mass[idx]);
        j1.energyCorr = j_energyCorr;
        j1.nConst = j_nConst;
      } else if (nJets30 == 2) {
        j2.p4 = P4f(j_pt, j_eta, a_phi[idx], a_mass[idx]);
        j2.energyCorr = j_energyCorr;
        j2.nConst = j_nConst;
      }
    }

    H1("L1SAK4CaloJet_passSelBx")->Fill(0.5, wgt);

    if (nJets30 >= 2) {
      H1("L1SAK4CaloJet_passSelBx_passDiJet30")->Fill(0.5, wgt);

      H1("L1SAK4CaloJet_nJets30")->Fill(nJets30, wgt);
      H1("L1SAK4CaloJet_nJets40")->Fill(nJets40, wgt);
      H1("L1SAK4CaloJet_nJets50")->Fill(nJets50, wgt);

      H1("L1SAK4CaloJet_J1_pt")->Fill(j1.p4.pt(), wgt);
      H1("L1SAK4CaloJet_J1_eta")->Fill(j1.p4.eta(), wgt);
      H2("L1SAK4CaloJet_J1_eta_phi")->Fill(j1.p4.eta(), j1.p4.phi(), wgt);
      H1("L1SAK4CaloJet_J1_phi")->Fill(j1.p4.phi(), wgt);
      H1("L1SAK4CaloJet_J1_mass")->Fill(j1.p4.mass(), wgt);
      H1("L1SAK4CaloJet_J1_energyCorr")->Fill(j1.energyCorr, wgt);
      H1("L1SAK4CaloJet_J1_nConst")->Fill(j1.nConst, wgt);

      H1("L1SAK4CaloJet_J2_pt")->Fill(j2.p4.pt(), wgt);
      H1("L1SAK4CaloJet_J2_eta")->Fill(j2.p4.eta(), wgt);
      H2("L1SAK4CaloJet_J2_eta_phi")->Fill(j2.p4.eta(), j2.p4.phi(), wgt);
      H1("L1SAK4CaloJet_J2_phi")->Fill(j2.p4.phi(), wgt);
      H1("L1SAK4CaloJet_J2_mass")->Fill(j2.p4.mass(), wgt);
      H1("L1SAK4CaloJet_J2_energyCorr")->Fill(j2.energyCorr, wgt);
      H1("L1SAK4CaloJet_J2_nConst")->Fill(j2.nConst, wgt);

      auto const j1j2_p4{j1.p4 + j2.p4};

      H1("L1SAK4CaloJet_J1J2_pt")->Fill(j1j2_p4.pt(), wgt);
      H1("L1SAK4CaloJet_J1J2_eta")->Fill(j1j2_p4.eta(), wgt);
      H1("L1SAK4CaloJet_J1J2_phi")->Fill(j1j2_p4.phi(), wgt);
      H1("L1SAK4CaloJet_J1J2_mass")->Fill(j1j2_p4.mass(), wgt);

      H1("L1SAK4CaloJet_J1J2_deltaY")->Fill(j1.p4.Rapidity() - j2.p4.Rapidity(), wgt);
      H1("L1SAK4CaloJet_J1J2_deltaEta")->Fill(j1.p4.eta() - j2.p4.eta(), wgt);
      H1("L1SAK4CaloJet_J1J2_deltaPhi")->Fill(utils::deltaPhi(j1.p4.phi(), j2.p4.phi()), wgt);
    }
  }
}
