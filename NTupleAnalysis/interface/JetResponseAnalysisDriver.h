#ifndef L1ScoutingTools_NTupleAnalysis_JetResponseAnalysisDriver_h
#define L1ScoutingTools_NTupleAnalysis_JetResponseAnalysisDriver_h

#include <functional>
#include <map>
#include <string>
#include <vector>

#include "L1ScoutingTools/NTupleAnalysis/interface/JetPerformanceAnalysisDriver.h"

class JetResponseAnalysisDriver : public JetPerformanceAnalysisDriver {
public:
  explicit JetResponseAnalysisDriver(const std::string& outputFilePath = "",
                                     const std::string& outputFileMode = "recreate")
      : JetPerformanceAnalysisDriver(outputFilePath, outputFileMode) {}

  explicit JetResponseAnalysisDriver(const std::string& tfile,
                                     const std::string& ttree,
                                     const std::string& outputFilePath,
                                     const std::string& outputFileMode = "recreate")
      : JetPerformanceAnalysisDriver(tfile, ttree, outputFilePath, outputFileMode) {}

  ~JetResponseAnalysisDriver() override {}

  void init() override;
  void analyze() override;

protected:
  std::map<std::string, std::function<bool(float, int)>> jetCategoryForJECFuncMap_;

  std::vector<std::string> jetCategoryLabelsForJECHistos(std::string const&, std::string const&) const;

  void bookHistograms_Jets(const std::string& dir,
                           const std::string& jetType,
                           const std::vector<std::string>& matchLabels = {}) override;

  void fillHistograms_Jets(const std::string& dir,
                           const fillHistoDataJets& fhDataJets,
                           float const weight = 1.f) override;
};

#endif
