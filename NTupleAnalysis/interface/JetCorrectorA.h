#ifndef L1ScoutingTools_NTupleAnalysis_JetCorrectorA_h
#define L1ScoutingTools_NTupleAnalysis_JetCorrectorA_h

#include <string>

#include "TGraph.h"

class JetCorrectorA {
public:
  explicit JetCorrectorA();
  void init(std::string const& filePath);
  float correction(float const pt, float const eta) const;

private:
  TGraph* gJEC_pt7p5_eta0p0to0p3_;
  TGraph* gJEC_pt7p5_eta0p3to0p6_;
  TGraph* gJEC_pt7p5_eta0p6to0p9_;
  TGraph* gJEC_pt7p5_eta0p9to1p2_;
  TGraph* gJEC_pt7p5_eta1p2to1p5_;
  TGraph* gJEC_pt7p5_eta1p5to1p8_;
  TGraph* gJEC_pt7p5_eta1p8to2p1_;
  TGraph* gJEC_pt7p5_eta2p1to2p4_;
};

#endif
