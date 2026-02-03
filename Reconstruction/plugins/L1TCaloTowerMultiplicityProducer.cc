#include <cmath>
#include <memory>
#include <utility>

#include "DataFormats/L1TCalorimeter/interface/CaloTower.h"
#include "DataFormats/L1Trigger/interface/Jet.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"

class L1TCaloTowerMultiplicityProducer : public edm::global::EDProducer<> {
public:
  explicit L1TCaloTowerMultiplicityProducer(edm::ParameterSet const&);

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override;

  edm::EDGetTokenT<l1t::CaloTowerBxCollection> const srcToken_;
  int const bunchCrossing_;
  int const towerMinHwPt_;
  int const towerMaxHwPt_;
  int const towerMinAbsHwEta_;
  int const towerMaxAbsHwEta_;
};

L1TCaloTowerMultiplicityProducer::L1TCaloTowerMultiplicityProducer(edm::ParameterSet const& iConfig)
    : srcToken_{consumes(iConfig.getParameter<edm::InputTag>("src"))},
      bunchCrossing_{iConfig.getParameter<int>("bunchCrossing")},
      towerMinHwPt_{iConfig.getParameter<int>("towerMinHwPt")},
      towerMaxHwPt_{iConfig.getParameter<int>("towerMaxHwPt")},
      towerMinAbsHwEta_{iConfig.getParameter<int>("towerMinAbsHwEta")},
      towerMaxAbsHwEta_{iConfig.getParameter<int>("towerMaxAbsHwEta")} {
  produces<int>();
}

void L1TCaloTowerMultiplicityProducer::produce(edm::StreamID, edm::Event& iEvent, edm::EventSetup const&) const {
  auto const& inputs = iEvent.get(srcToken_);

  int ret_value{0};

  for (auto bx = inputs.getFirstBX(); bx <= inputs.getLastBX(); ++bx) {
    if (bx != bunchCrossing_) {
      continue;
    }

    auto const nInputs = inputs.size(bx);
    for (auto idx = 0u; idx < nInputs; ++idx) {
      auto const& input = inputs.at(bx, idx);
      auto const absHwEta = std::abs(input.hwEta());
      if ((towerMinHwPt_ < 0 or input.hwPt() >= towerMinHwPt_) and
          (towerMaxHwPt_ < 0 or input.hwPt() <= towerMaxHwPt_) and
          (towerMinAbsHwEta_ < 0 or absHwEta >= towerMinAbsHwEta_) and
          (towerMaxAbsHwEta_ < 0 or absHwEta <= towerMaxAbsHwEta_)) {
        ++ret_value;
      }
    }
  }

  LogTrace("L1TCaloTowerMultiplicityProducer") << "[L1TCaloTowerMultiplicityProducer] ["
                                               << moduleDescription().moduleLabel() << "] output value = " << ret_value;

  auto output = std::make_unique<int>(ret_value);
  iEvent.put(std::move(output));
}

void L1TCaloTowerMultiplicityProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("src")->setComment("Input product (type: l1t::CaloTowerBxCollection)");
  desc.add<int>("bunchCrossing", 0)->setComment("BX value");
  desc.add<int>("towerMinHwPt", -1)->setComment("Min hwPt (inclusive) of l1t::CaloTowers (ignored if negative)");
  desc.add<int>("towerMaxHwPt", -1)->setComment("Max hwPt (inclusive) of l1t::CaloTowers (ignored if negative)");
  desc.add<int>("towerMinAbsHwEta", -1)->setComment("Min |hwEta| (inclusive) of l1t::CaloTowers (ignored if negative)");
  desc.add<int>("towerMaxAbsHwEta", -1)->setComment("Max |hwEta| (inclusive) of l1t::CaloTowers (ignored if negative)");

  descriptions.add("l1tCaloTowerMultiplicityProducer", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(L1TCaloTowerMultiplicityProducer);
