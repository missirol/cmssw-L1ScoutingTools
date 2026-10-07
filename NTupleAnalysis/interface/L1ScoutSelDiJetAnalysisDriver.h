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
    int index = -1;
    float energyCorr = 0.f;
    float energyFracEm = 0.f;
    int nConst = 0;
  };

  bool bxFilterDijetEt30() const;

  void fill_dijet_plots(std::string const& plot_label,
                        float const wgt,
                        unsigned int const nJets30,
                        unsigned int const nJets40,
                        unsigned int const nJets50,
                        Jet const& j1,
                        Jet const& j2,
                        bool const fillExtraJetVars,
                        float const minDijetMass,
                        float const maxDijetDeltaRapAbs,
                        float const minDijetDeltaPhiAbs);
};

#endif
