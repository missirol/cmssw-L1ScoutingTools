#ifndef L1ScoutingTools_NTupleAnalysis_JetMETPerformanceAnalysisDriver_h
#define L1ScoutingTools_NTupleAnalysis_JetMETPerformanceAnalysisDriver_h

#include <functional>
#include <map>
#include <string>
#include <vector>

#include "L1ScoutingTools/NTupleAnalysis/interface/AnalysisDriverBase.h"
#include "L1ScoutingTools/NTupleAnalysis/interface/JetCorrectorA.h"

class JetMETPerformanceAnalysisDriver : public AnalysisDriverBase {
public:
  explicit JetMETPerformanceAnalysisDriver(const std::string& outputFilePath = "",
                                           const std::string& outputFileMode = "recreate");
  explicit JetMETPerformanceAnalysisDriver(const std::string& tfile,
                                           const std::string& ttree,
                                           const std::string& outputFilePath,
                                           const std::string& outputFileMode = "recreate");
  ~JetMETPerformanceAnalysisDriver() override {}

  void init() override;
  void analyze() override;

protected:
  JetCorrectorA jecA_;

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

  class fillHistoDataMET {
  public:
    std::string metCollection = "";

    struct Match {
      Match(const std::string& theLabel, const std::string& theMETCollection)
          : label(theLabel), metCollection(theMETCollection) {}
      std::string label;
      std::string metCollection;
    };
    std::vector<Match> matches;
  };

  virtual void bookHistograms_Jets(const std::string& dir,
                                   const std::string& jetType,
                                   const std::vector<std::string>& matchLabels = {});
  void bookHistograms_MET(const std::string& dir,
                          const std::string& metType,
                          const std::vector<std::string>& matchLabels = {});

  virtual void fillHistograms_Jets(const std::string& dir,
                                   const fillHistoDataJets& fhDataJets,
                                   float const weight = 1.f);
  void fillHistograms_MET(const std::string& dir, const fillHistoDataMET& fhDataMET, float const weight = 1.f);

  void bookHistograms_Jets_2DMaps(const std::string& dir, const std::string& jetType1, const std::string& jetType2);
  void bookHistograms_MET_2DMaps(const std::string& dir,
                                 const std::string& metType1,
                                 const std::string& metType2,
                                 bool const book1D = false);

  void fillHistograms_Jets_2DMaps(const std::string& dir,
                                  const fillHistoDataJets& fhDataJets1,
                                  const fillHistoDataJets& fhDataJets2,
                                  float const weight = 1.f);
  void fillHistograms_MET_2DMaps(const std::string& dir,
                                 const fillHistoDataMET& fhDataMET1,
                                 const fillHistoDataMET& fhDataMET2,
                                 bool const fill1D = false,
                                 float const weight = 1.f);

  std::map<std::string, std::map<std::string, std::string>> labelMap_jetAK4_;
  std::map<std::string, std::map<std::string, std::string>> labelMap_jetAK8_;
  std::map<std::string, std::map<std::string, std::string>> labelMap_MET_;
};

#endif
