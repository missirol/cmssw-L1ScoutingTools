#include <algorithm>
#include <cmath>
#include <fstream>
#include <memory>
#include <numeric>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "CommonTools/Utils/interface/FormulaEvaluator.h"
#include "DataFormats/L1Trigger/interface/Jet.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "FWCore/Utilities/interface/FileInPath.h"

class L1TCaloTowerJetCorrector : public edm::global::EDProducer<> {
public:
  explicit L1TCaloTowerJetCorrector(edm::ParameterSet const&);

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override;

  class JetCorrector {
  public:
    explicit JetCorrector(std::string const& filePath) {
      ifstream infile(filePath);
      std::string line{};
      while (std::getline(infile, line)) {
        std::istringstream iss(line);

        float ptMin{0.f}, ptMax{0.f}, absEtaMin{0.f}, absEtaMax{0.f};
        int puProxyMin{0}, puProxyMax{0}, formNParams{0};
        std::string formEvalStr{""};

        if (!(iss >> ptMin >> ptMax >> absEtaMin >> absEtaMax >> puProxyMin >> puProxyMax >> formEvalStr >>
              formNParams)) {
          throw cms::Exception("InvalidInput")
              << "failed to read line from input file (invalid format): \"" << line << "\"";
        }

        reco::FormulaEvaluator formEval{formEvalStr};

        std::vector<double> formParams(formNParams);
        for (auto idx = 0; idx < formNParams; ++idx) {
          if (!(iss >> formParams[idx])) {
            throw cms::Exception("InvalidInput")
                << "failed to read line from input file (invalid format, formula parameter #" << idx << "): \"" << line
                << "\"";
          }
        }

        data_.emplace_back(
            ptMin, ptMax, absEtaMin, absEtaMax, puProxyMin, puProxyMax, std::move(formEval), std::move(formParams));
      }
    }

    double correction(float const pt, float const absEta, int const puProxy) const {
      for (auto const& entry : data_) {
        if ((entry.absEtaMin < 0 or absEta >= entry.absEtaMin) and (entry.absEtaMax < 0 or absEta < entry.absEtaMax) and
            (entry.puProxyMin < 0 or puProxy >= entry.puProxyMin) and
            (entry.puProxyMax < 0 or puProxy < entry.puProxyMax)) {
          std::vector<double> vars{std::min(std::max(pt, entry.ptMin), entry.ptMax)};
          return entry.formulaEvaluator.evaluate(vars, entry.formulaParameters);
        }
      }
      return 0;
    }

  private:
    struct Entry {
      float ptMin;
      float ptMax;
      float absEtaMin;
      float absEtaMax;
      int puProxyMin;
      int puProxyMax;
      reco::FormulaEvaluator formulaEvaluator;
      std::vector<double> formulaParameters;
    };

    std::vector<Entry> data_;
  };

  edm::EDGetTokenT<l1t::JetBxCollection> const srcToken_;
  edm::EDGetTokenT<int> const puProxyToken_;
  JetCorrector const jetCorrector_;
  int const bxMin_;
  int const bxMax_;
};

L1TCaloTowerJetCorrector::L1TCaloTowerJetCorrector(edm::ParameterSet const& iConfig)
    : srcToken_{consumes(iConfig.getParameter<edm::InputTag>("src"))},
      puProxyToken_{consumes(iConfig.getParameter<edm::InputTag>("puProxy"))},
      jetCorrector_{iConfig.getParameter<edm::FileInPath>("jecFile").fullPath()},
      bxMin_{iConfig.getParameter<int>("bxMin")},
      bxMax_{iConfig.getParameter<int>("bxMax")} {
  produces<l1t::JetBxCollection>();
}

void L1TCaloTowerJetCorrector::produce(edm::StreamID, edm::Event& iEvent, edm::EventSetup const&) const {
  auto const& inputs = iEvent.get(srcToken_);

  auto const& puProxy = iEvent.get(puProxyToken_);

  auto const bxMin = std::max(bxMin_, inputs.getFirstBX());
  auto const bxMax = std::min(bxMax_, inputs.getLastBX());

  auto output = std::make_unique<l1t::JetBxCollection>(0, bxMin, bxMax);

  for (auto bx = bxMin; bx <= bxMax; ++bx) {
    auto const nInputs = inputs.size(bx);

    std::vector<l1t::Jet> out_jets{};
    out_jets.reserve(nInputs);
    for (auto idx = 0u; idx < nInputs; ++idx) {
      auto jet = inputs.at(bx, idx);
      auto const corr{jetCorrector_.correction(jet.pt(), std::abs(jet.eta()), puProxy)};

      LogTrace("L1TCaloTowerJetCorrector")
          << "[L1TCaloTowerJetCorrector] Jet(bx=" << bx << ", index=" << idx << ") (PU proxy = " << puProxy << ")";

      LogTrace("L1TCaloTowerJetCorrector")
          << "[L1TCaloTowerJetCorrector]    Pre -JESC: eta=" << jet.eta() << " phi=" << jet.phi()
          << " pT(uncorrected)=" << jet.pt() << " JESC=" << corr;

      jet.setP4(jet.p4() * corr);

      LogTrace("L1TCaloTowerJetCorrector") << "[L1TCaloTowerJetCorrector]    Post-JESC: eta=" << jet.eta()
                                           << " phi=" << jet.phi() << " pT(corrected)=" << jet.pt();

      if (corr > 0) {
        out_jets.emplace_back(std::move(jet));
      }
    }

    std::vector<size_t> sortIdxs(out_jets.size());
    std::iota(sortIdxs.begin(), sortIdxs.end(), 0);
    std::sort(sortIdxs.begin(), sortIdxs.end(), [&](size_t const i1, size_t const i2) {
      return out_jets[i1].pt() > out_jets[i2].pt();
    });

    for (auto idx : sortIdxs) {
      output->push_back(bx, out_jets[idx]);
    }
  }

  iEvent.put(std::move(output));
}

void L1TCaloTowerJetCorrector::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("src")->setComment("Input product for jets (type: l1t::JetBxCollection)");
  desc.add<edm::InputTag>("puProxy")->setComment("Input product for PU-proxy value (type: int)");
  desc.add<edm::FileInPath>("jecFile")->setComment("Path to text file containing jet-energy-scale corrections");
  desc.add<int>("bxMin", -2)->setComment("Min BX (inclusive)");
  desc.add<int>("bxMax", 2)->setComment("Max BX (inclusive)");

  descriptions.add("l1tCaloTowerJetCorrector", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(L1TCaloTowerJetCorrector);
