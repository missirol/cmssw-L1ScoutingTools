#ifndef L1ScoutingTools_NTupleAnalysis_JetPerformanceAnalysisDriver_h
#define L1ScoutingTools_NTupleAnalysis_JetPerformanceAnalysisDriver_h

#include <functional>
#include <map>
#include <string>
#include <vector>

#include "L1ScoutingTools/NTupleAnalysis/interface/AnalysisDriverBase.h"
#include "L1ScoutingTools/NTupleAnalysis/interface/JetCorrectorA.h"

class JetPerformanceAnalysisDriver : public AnalysisDriverBase {
public:
  explicit JetPerformanceAnalysisDriver(const std::string& outputFilePath = "",
                                        const std::string& outputFileMode = "recreate");
  explicit JetPerformanceAnalysisDriver(const std::string& tfile,
                                        const std::string& ttree,
                                        const std::string& outputFilePath,
                                        const std::string& outputFileMode = "recreate");
  ~JetPerformanceAnalysisDriver() override {}

  void init() override;
  void analyze() override;

protected:
  std::vector<std::string> jetCategoryLabels_;
  bool jetBelongsToCategory(const std::string& categLabel,
                            const float jetPt,
                            const float jetAbsEta,
                            const unsigned int nCTie4) const;

  class fillHistoDataJets {
  public:
    std::string jetCollection = "";
    float jetPtMin = -1.;
    float jetPtMax = -1.;
    float jetAbsEtaMax = -1.;

    struct Match {
      Match(const std::string& theLabel,
            const std::string& theJetCollection,
            const float theJetPtMin,
            const float theJetPtMax,
            const float theJetDeltaRMin)
          : label(theLabel),
            jetCollection(theJetCollection),
            jetPtMin(theJetPtMin),
            jetPtMax(theJetPtMax),
            jetDeltaRMin(theJetDeltaRMin) {}
      std::string label;
      std::string jetCollection;
      float jetPtMin;
      float jetPtMax;
      float jetDeltaRMin;
    };
    std::vector<Match> matches;
  };

  virtual void bookHistograms_Jets(const std::string& dir,
                                   const std::string& jetType,
                                   const std::vector<std::string>& matchLabels = {});

  virtual void fillHistograms_Jets(const std::string& dir,
                                   const fillHistoDataJets& fhDataJets,
                                   float const weight = 1.f);

  virtual bool passJetId(std::string const& jetCollName,
                         int const nConst,
                         float const pt,
                         float const energyCorr,
                         float const energyFracEm,
                         unsigned int const nConstSatECALOrHCAL) const;

  virtual std::string jetCollectionBranchName(std::string const& jetCollName) const;

  std::map<std::string, std::map<std::string, std::string>> labelMap_jetAK4_;
};

#endif
