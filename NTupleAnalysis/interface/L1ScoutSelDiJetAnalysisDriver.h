#ifndef L1ScoutingTools_NTupleAnalysis_L1ScoutSelDiJetAnalysisDriver_h
#define L1ScoutingTools_NTupleAnalysis_L1ScoutSelDiJetAnalysisDriver_h

#include <string>
#include <vector>

#include <Math/PtEtaPhiM4D.h>
#include <Math/LorentzVector.h>

#include "L1ScoutingTools/NTupleAnalysis/interface/AnalysisDriverBase.h"

class L1ScoutSelDiJetAnalysisDriver : public AnalysisDriverBase {
public:
  explicit L1ScoutSelDiJetAnalysisDriver(const std::string& outputFilePath = "",
                                         const std::string& outputFileMode = "recreate");
  explicit L1ScoutSelDiJetAnalysisDriver(const std::string& tfile,
                                         const std::string& ttree,
                                         const std::string& outputFilePath,
                                         const std::string& outputFileMode = "recreate");
  ~L1ScoutSelDiJetAnalysisDriver() override {}

  void init() override;
  void analyze() override;

protected:
  using P4f = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

  struct Jet {
    P4f p4;
    float energyCorr = -999;
    int nConst = -999;
  };
};

#endif
