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
  int selectionType_ = -1;

  using P4f = ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>;

  struct Jet {
    P4f p4;
    int index = -1;
    float energyCorr = 0.f;
    float energyFracEm = 0.f;
    int nConst = 0;
  };

  class dijetCut {
  public:
    explicit dijetCut(float const min_mjj = -1.f,
                      float const min_drap = -1.f,
                      float const max_drap = -1.f,
                      float const min_dphi = -1.f,
                      float const max_dphi = -1.f)
        : min_mjj_{min_mjj},
          min_absDeltaRap_{min_drap},
          max_absDeltaRap_{max_drap},
          min_absDeltaPhi_{min_dphi},
          max_absDeltaPhi_{max_dphi} {}

    bool operator()(float const mjj, float const absDeltaRap, float const absDeltaPhi) const {
      return (min_mjj_ < 0.f or mjj > min_mjj_) and (min_absDeltaRap_ < 0.f or absDeltaRap >= min_absDeltaRap_) and
             (max_absDeltaRap_ < 0.f or absDeltaRap < max_absDeltaRap_) and
             (min_absDeltaPhi_ < 0.f or absDeltaPhi >= min_absDeltaPhi_) and
             (max_absDeltaPhi_ < 0.f or absDeltaPhi < max_absDeltaPhi_);
    }

  private:
    float const min_mjj_;
    float const min_absDeltaRap_;
    float const max_absDeltaRap_;
    float const min_absDeltaPhi_;
    float const max_absDeltaPhi_;
  };

  std::unordered_map<std::string, dijetCut const> sr_sel_map_;

  bool bxFilterDijetEt30() const;

  void fill_plots_l1tJets(float const wgt, int const selectionType);
  void fill_plots_l1sCaloJets(float const wgt, int const selectionType);

  void fill_dijet_plots(std::string const& plot_label,
                        float const wgt,
                        unsigned int const nJets30,
                        unsigned int const nJets40,
                        unsigned int const nJets50,
                        Jet const& j1,
                        Jet const& j2,
                        bool const fillExtraJetVars,
                        dijetCut const& dijet_cut);
};

#endif
