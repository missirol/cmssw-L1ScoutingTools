#ifndef L1ScoutingTools_NTupleAnalysis_AnalysisDriverBase_h
#define L1ScoutingTools_NTupleAnalysis_AnalysisDriverBase_h

#include <map>
#include <memory>
#include <string>
#include <vector>
#include <sstream>
#include <stdexcept>
#include <typeinfo>
#include <TFile.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TH3D.h>

class AnalysisDriverBase {
public:
  explicit AnalysisDriverBase(const std::string& outputFilePath = "", const std::string& outputFileMode = "recreate");
  explicit AnalysisDriverBase(const std::string& tfile,
                              const std::string& ttree,
                              const std::string& outputFilePath,
                              const std::string& outputFileMode = "recreate");
  virtual ~AnalysisDriverBase() {}

  int setInputTTree(const std::string& tfile, const std::string& ttree);

  virtual void init() = 0;
  virtual void analyze() = 0;
  virtual void write(TFile&);

  virtual void process(const Long64_t firstEntry = 0, const Long64_t maxEntries = -1);
  virtual void writeToFile(const std::string& output_file, const std::string& output_mode);

  void setOutputFilePath(const std::string& foo) { outputFilePath_ = foo; }
  void setOutputFileMode(const std::string& foo) { outputFileMode_ = foo; }

  void setVerbosity(const int foo) { verbosity_ = foo; }
  int getVerbosity() const { return verbosity_; }

  Long64_t eventsProcessed() const { return eventsProcessed_; }

  bool hasTTreeReaderValue(const std::string& key) const {
    return (map_TTreeReaderValues_.find(key) != map_TTreeReaderValues_.end());
  }

  template <class T>
  T const* value_ptr(const std::string& key) const;
  template <class T>
  T const& value(const std::string& key) const;

  template <class T>
  TTreeReaderArray<T> const* array_ptr(const std::string& key) const;
  template <class T>
  TTreeReaderArray<T> const& array(const std::string& key) const;

  template <class T>
  std::vector<T> const* vector_ptr(const std::string& key) const;
  template <class T>
  std::vector<T> const& vector(const std::string& key) const;

  virtual void addOption(const std::string& key, const std::string& opt);
  virtual bool hasOption(const std::string& key) const { return (map_options_.find(key) != map_options_.end()); }
  virtual std::string const& getOption(const std::string& key) const;

  bool hasTH1D(const std::string& key) const { return (mapTH1D_.find(key) != mapTH1D_.end()); }
  bool hasTH2D(const std::string& key) const { return (mapTH2D_.find(key) != mapTH2D_.end()); }
  bool hasTH3D(const std::string& key) const { return (mapTH3D_.find(key) != mapTH3D_.end()); }

protected:
  std::unique_ptr<TFile> theFile_;
  std::unique_ptr<TTreeReader> theReader_;

  std::string outputFilePath_ = "";
  std::string outputFileMode_ = "recreate";

  int verbosity_ = 0;
  Long64_t eventsProcessed_ = 0;

  std::map<std::string, std::unique_ptr<ROOT::Internal::TTreeReaderValueBase>> map_TTreeReaderValues_;
  std::map<std::string, std::string> map_options_;

  TH1D* H1(const std::string&);
  TH2D* H2(const std::string&);
  TH3D* H3(const std::string&);

  void addTH1D(const std::string&, int const, float const, float const);
  void addTH1D(const std::string&, const std::vector<float>&);
  void addTH2D(const std::string&, int const, float const, float const, int const, float const, float const);
  void addTH2D(const std::string&, const std::vector<float>&, const std::vector<float>&);
  void addTH3D(const std::string&, const std::vector<float>&, const std::vector<float>&, const std::vector<float>&);

  std::map<std::string, std::unique_ptr<TH1D>> mapTH1D_;
  std::map<std::string, std::unique_ptr<TH2D>> mapTH2D_;
  std::map<std::string, std::unique_ptr<TH3D>> mapTH3D_;

  std::vector<std::string> outputKeys_;
};

template <class T>
T const* AnalysisDriverBase::value_ptr(const std::string& key) const {
  if (not hasTTreeReaderValue(key)) {
    return nullptr;
  }

  auto* ptr = dynamic_cast<TTreeReaderValue<T>*>(map_TTreeReaderValues_.at(key).get());

  if (ptr == nullptr) {
    return nullptr;
  }

  return ptr->Get();
}

template <class T>
T const& AnalysisDriverBase::value(const std::string& key) const {
  auto const* ptr = value_ptr<T>(key);

  if (ptr == nullptr) {
    std::ostringstream ss_str;
    if (not hasTTreeReaderValue(key)) {
      ss_str << "value -- no branch named \"" << key << "\".";
    } else {
      ss_str << "value -- dynamic_cast to \"TTreeReaderValue<"
             << typeid(T).name() << ">*\" failed for key \"" << key << "\".";
    }
    throw std::runtime_error(ss_str.str());
  }

  return *ptr;
}

template <class T>
TTreeReaderArray<T> const* AnalysisDriverBase::array_ptr(const std::string& key) const {
  if (not hasTTreeReaderValue(key)) {
    return nullptr;
  }

  auto* ptr = dynamic_cast<TTreeReaderArray<T>*>(map_TTreeReaderValues_.at(key).get());

  if (ptr == nullptr) {
    return nullptr;
  }

  return ptr;
}

template <class T>
TTreeReaderArray<T> const& AnalysisDriverBase::array(const std::string& key) const {
  auto const* ptr = array_ptr<T>(key);

  if (ptr == nullptr) {
    std::ostringstream ss_str;
    if (not hasTTreeReaderValue(key)) {
      ss_str << "array -- no branch named \"" << key << "\".";
    } else {
      ss_str << "array -- dynamic_cast to \"TTreeReaderValue<"
             << typeid(T).name() << ">*\" failed for key \"" << key << "\".";
    }
    throw std::runtime_error(ss_str.str());
  }

  return *ptr;
}

template <class T>
std::vector<T> const* AnalysisDriverBase::vector_ptr(const std::string& key) const {
  if (not hasTTreeReaderValue(key)) {
    return nullptr;
  }

  auto* ptr = dynamic_cast<TTreeReaderValue<std::vector<T>>*>(map_TTreeReaderValues_.at(key).get());

  if (ptr == nullptr) {
    return nullptr;
  }

  return ptr->Get();
}

template <class T>
std::vector<T> const& AnalysisDriverBase::vector(const std::string& key) const {
  auto const* ptr = vector_ptr<T>(key);

  if (ptr == nullptr) {
    std::ostringstream ss_str;
    if (not hasTTreeReaderValue(key)) {
      ss_str << "vector -- no branch named \"" << key << "\".";
    } else {
      ss_str << "vector -- dynamic_cast to \"TTreeReaderValue<std::vector<"
             << typeid(T).name() << ">>*\" failed for key \"" << key << "\".";
    }
    throw std::runtime_error(ss_str.str());
  }

  return *ptr;
}

#endif
