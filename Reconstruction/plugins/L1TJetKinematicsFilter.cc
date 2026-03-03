#include <cmath>

#include "DataFormats/L1Trigger/interface/Jet.h"
#include "FWCore/Framework/interface/global/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"

class L1TJetKinematicsFilter : public edm::global::EDFilter<> {
public:
  explicit L1TJetKinematicsFilter(edm::ParameterSet const&);

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  bool filter(edm::StreamID, edm::Event&, edm::EventSetup const&) const override;

  edm::EDGetTokenT<l1t::JetBxCollection> const srcToken_;
  int const bxMin_;
  int const bxMax_;
  int const nMin_;
  double const ptMin_;
  double const absEtaMin_;
  double const absEtaMax_;
};

L1TJetKinematicsFilter::L1TJetKinematicsFilter(edm::ParameterSet const& iConfig)
    : srcToken_{consumes(iConfig.getParameter<edm::InputTag>("src"))},
      bxMin_{iConfig.getParameter<int>("bxMin")},
      bxMax_{iConfig.getParameter<int>("bxMax")},
      nMin_{iConfig.getParameter<int>("nMin")},
      ptMin_{iConfig.getParameter<double>("ptMin")},
      absEtaMin_{iConfig.getParameter<double>("absEtaMin")},
      absEtaMax_{iConfig.getParameter<double>("absEtaMax")} {}

bool L1TJetKinematicsFilter::filter(edm::StreamID, edm::Event& iEvent, edm::EventSetup const&) const {
  auto const& inputs = iEvent.get(srcToken_);

  auto const bxMin = std::max(bxMin_, inputs.getFirstBX());
  auto const bxMax = std::min(bxMax_, inputs.getLastBX());

  int nJets{0};

  for (auto bx = bxMin; bx <= bxMax; ++bx) {
    auto const nInputs = inputs.size(bx);
    for (auto idx = 0u; idx < nInputs; ++idx) {
      auto jet = inputs.at(bx, idx);
      auto const jetAbsEta = std::abs(jet.eta());
      if ((absEtaMin_ < 0 or jetAbsEta > absEtaMin_) and
          (absEtaMax_ < 0 or jetAbsEta < absEtaMax_) and jet.pt() > ptMin_) {
        ++nJets;
      }
    }
  }

  return (nJets >= nMin_);
}

void L1TJetKinematicsFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("src")->setComment("Input jets (type: l1t::JetBxCollection)");
  desc.add<int>("bxMin", 0)->setComment("Min BX (inclusive)");
  desc.add<int>("bxMax", 0)->setComment("Max BX (inclusive)");
  desc.add<int>("nMin", 0)->setComment("Min number of jets required to pass pT and |eta| selections (inclusive)");
  desc.add<double>("ptMin", 1)->setComment("Min jet pT");
  desc.add<double>("absEtaMin", -1)->setComment("Min jet |eta| (ignored if negative)");
  desc.add<double>("absEtaMax", -1)->setComment("Max jet |eta| (ignored if negative)");

  descriptions.add("l1tJetKinematicsFilter", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(L1TJetKinematicsFilter);
