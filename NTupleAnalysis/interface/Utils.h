#ifndef L1ScoutingTools_NTupleAnalysis_Utils_h
#define L1ScoutingTools_NTupleAnalysis_Utils_h

#include <cmath>
#include <string>
#include <vector>
#include <map>

namespace utils {

  // https://github.com/cms-sw/cmssw/blob/589c31dab3371f37ce31713a8195d7c0de3f111b/DataFormats/Math/interface/deltaPhi.h#L16-L24
  constexpr float deltaPhi(const float phi1, const float phi2) {
    float const bare_dphi = phi1 - phi2;
    if (std::abs(bare_dphi) <= float(M_PI)) {
      return bare_dphi;
    }
    constexpr float o2pi = 1.f / (2.f * M_PI);
    float const bare_dphi_o2pi = std::round(bare_dphi * o2pi);
    return bare_dphi - bare_dphi_o2pi * float(2.f * M_PI);
  }

  constexpr float deltaR2(const float eta1, const float phi1, const float eta2, const float phi2) {
    auto const dphi{deltaPhi(phi1, phi2)};
    return ((eta1 - eta2) * (eta1 - eta2)) + (dphi * dphi);
  }

  std::vector<std::string> stringTokens(const std::string&, const std::string&);
  bool stringContains(const std::string& str, const std::string& substr);
  bool stringStartsWith(const std::string& str, const std::string& substr);
  bool stringEndsWith(const std::string& str, const std::string& substr);

  template <typename T1, typename T2>
  std::vector<T1> mapKeys(std::map<T1, T2> const&);
}  // namespace utils

template <typename T1, typename T2>
std::vector<T1> utils::mapKeys(std::map<T1, T2> const& aMap) {
  std::vector<T1> ret;
  ret.reserve(aMap.size());
  for (auto const& mapEntry : aMap) {
    ret.emplace_back(mapEntry.first);
  }

  return ret;
}

#endif
