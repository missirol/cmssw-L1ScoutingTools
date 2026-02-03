#include <cmath>

#include "L1ScoutingTools/NTupleAnalysis/interface/JetCorrectorA.h"

#include "TFile.h"

JetCorrectorA::JetCorrectorA() {
  gJEC_pt7p5_eta0p0to0p3_ = nullptr;
  gJEC_pt7p5_eta0p3to0p6_ = nullptr;
  gJEC_pt7p5_eta0p6to0p9_ = nullptr;
  gJEC_pt7p5_eta0p9to1p2_ = nullptr;
  gJEC_pt7p5_eta1p2to1p5_ = nullptr;
  gJEC_pt7p5_eta1p5to1p8_ = nullptr;
  gJEC_pt7p5_eta1p8to2p1_ = nullptr;
  gJEC_pt7p5_eta2p1to2p4_ = nullptr;
}

void JetCorrectorA::init(std::string const& filePath) {
  auto* tfile = TFile::Open(filePath.c_str());
  if (tfile == nullptr) {
    throw std::runtime_error("Invalid path to input file: " + filePath);
  }

  gJEC_pt7p5_eta0p0to0p3_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta0p3"));
  gJEC_pt7p5_eta0p3to0p6_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta0p3to0p6"));
  gJEC_pt7p5_eta0p6to0p9_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta0p6to0p9"));
  gJEC_pt7p5_eta0p9to1p2_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta0p9to1p2"));
  gJEC_pt7p5_eta1p2to1p5_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta1p2to1p5"));
  gJEC_pt7p5_eta1p5to1p8_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta1p5to1p8"));
  gJEC_pt7p5_eta1p8to2p1_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta1p8to2p1"));
  gJEC_pt7p5_eta2p1to2p4_ = reinterpret_cast<TGraph*>(tfile->Get("Graph_JEC_pt7p5_eta2p1to2p4"));

  tfile->Close();
}

float JetCorrectorA::correction(float const pt, float const eta) const {
  float pt_corr{0.f};

  if (pt <= 0) {
    return pt_corr;
  }

  float const absEta{std::abs(eta)};

  if (absEta < 0.3) {
    pt_corr = gJEC_pt7p5_eta0p0to0p3_->Eval(pt);
  } else if (0.3 <= absEta and absEta < 0.6) {
    pt_corr = gJEC_pt7p5_eta0p3to0p6_->Eval(pt);
  } else if (0.6 <= absEta and absEta < 0.9) {
    pt_corr = gJEC_pt7p5_eta0p6to0p9_->Eval(pt);
  } else if (0.9 <= absEta and absEta < 1.2) {
    pt_corr = gJEC_pt7p5_eta0p9to1p2_->Eval(pt);
  } else if (1.2 <= absEta and absEta < 1.5) {
    pt_corr = gJEC_pt7p5_eta1p2to1p5_->Eval(pt);
  } else if (1.5 <= absEta and absEta < 1.8) {
    pt_corr = gJEC_pt7p5_eta1p5to1p8_->Eval(pt);
  } else if (1.8 <= absEta and absEta < 2.1) {
    pt_corr = gJEC_pt7p5_eta1p8to2p1_->Eval(pt);
  } else if (2.1 <= absEta and absEta < 2.4) {
    pt_corr = gJEC_pt7p5_eta2p1to2p4_->Eval(pt);
  }

  return (pt_corr > 0) ? (pt_corr / pt) : 0.f;
}
