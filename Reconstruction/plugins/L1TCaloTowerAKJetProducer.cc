#include <algorithm>
#include <memory>
#include <utility>
#include <vector>

#include "DataFormats/L1TCalorimeter/interface/CaloTower.h"
#include "DataFormats/L1Trigger/interface/Jet.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "L1Trigger/L1TCalorimeter/interface/CaloTools.h"

#include "fastjet/ClusterSequence.hh"
#include "fastjet/JetDefinition.hh"
#include "fastjet/PseudoJet.hh"

class L1TCaloTowerAKJetProducer : public edm::global::EDProducer<> {
public:
  explicit L1TCaloTowerAKJetProducer(edm::ParameterSet const&);

  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override;

  edm::EDGetTokenT<l1t::CaloTowerBxCollection> const srcToken_;
  int const bxMin_;
  int const bxMax_;
  int const towerMinHwPt_;
  int const towerMaxHwPt_;
  double const rParam_;
  double const jetPtMin_;
  fastjet::JetDefinition const fjJetDefinition_;
};

L1TCaloTowerAKJetProducer::L1TCaloTowerAKJetProducer(edm::ParameterSet const& iConfig)
    : srcToken_{consumes(iConfig.getParameter<edm::InputTag>("src"))},
      bxMin_{iConfig.getParameter<int>("bxMin")},
      bxMax_{iConfig.getParameter<int>("bxMax")},
      towerMinHwPt_{iConfig.getParameter<int>("towerMinHwPt")},
      towerMaxHwPt_{iConfig.getParameter<int>("towerMaxHwPt")},
      rParam_{iConfig.getParameter<double>("rParam")},
      jetPtMin_{iConfig.getParameter<double>("jetPtMin")},
      fjJetDefinition_{fastjet::antikt_algorithm, rParam_} {
  produces<l1t::JetBxCollection>();
}

void L1TCaloTowerAKJetProducer::produce(edm::StreamID, edm::Event& iEvent, edm::EventSetup const&) const {
  auto const& inputs = iEvent.get(srcToken_);

  auto const bxMin = std::max(bxMin_, inputs.getFirstBX());
  auto const bxMax = std::min(bxMax_, inputs.getLastBX());

  auto output = std::make_unique<l1t::JetBxCollection>(0, bxMin, bxMax);

  for (auto bx = bxMin; bx <= bxMax; ++bx) {
    auto const nInputs = inputs.size(bx);

    std::vector<fastjet::PseudoJet> fjInputs{};
    fjInputs.reserve(nInputs);
    for (auto idx = 0u; idx < nInputs; ++idx) {
      auto const& input = inputs.at(bx, idx);
      if ((towerMinHwPt_ < 0 or input.hwPt() >= towerMinHwPt_) and
          (towerMaxHwPt_ < 0 or input.hwPt() <= towerMaxHwPt_)) {
        auto const mpEta = l1t::CaloTools::mpEta(input.hwEta());
        auto const ctP4 = l1t::CaloTools::p4MP(input.hwPt(), mpEta, input.hwPhi());
        fjInputs.emplace_back(ctP4.px(), ctP4.py(), ctP4.pz(), ctP4.energy());
      }
    }

    auto const fjClusterSeq = fastjet::ClusterSequence{fjInputs, fjJetDefinition_};
    auto const fjJets = fastjet::sorted_by_pt(fjClusterSeq.inclusive_jets(jetPtMin_));

    for (auto const& fjJet : fjJets) {
      l1t::Jet::LorentzVector const p4{fjJet.px(), fjJet.py(), fjJet.pz(), fjJet.E()};
      output->push_back(bx, l1t::Jet{p4});
    }
  }

  iEvent.put(std::move(output));
}

void L1TCaloTowerAKJetProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;

  desc.add<edm::InputTag>("src")->setComment("Input product (type: l1t::CaloTowerBxCollection)");
  desc.add<int>("bxMin", -2)->setComment("Min BX (inclusive)");
  desc.add<int>("bxMax", 2)->setComment("Max BX (inclusive)");
  desc.add<int>("towerMinHwPt", 1)
      ->setComment("Min hwPt (inclusive) of l1t::CaloTowers used for jet clustering (ignored if negative)");
  desc.add<int>("towerMaxHwPt", -1)
      ->setComment("Max hwPt (inclusive) of l1t::CaloTowers used for jet clustering (ignored if negative)");
  desc.add<double>("rParam", 0.4)->setComment("R parameter for anti-kT clustering with FastJet");
  desc.add<double>("jetPtMin", 0)
      ->setComment("Minimum pT of output jets (argument of fastjet::ClusterSequence::inclusive_jets)");

  descriptions.add("l1tCaloTowerAKJetProducer", desc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(L1TCaloTowerAKJetProducer);
