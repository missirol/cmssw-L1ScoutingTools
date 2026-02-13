#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <random>
#include <string>

class Object {
public:
  Object(int a, int b, int c, int d, int e)
    : a_(a), b_(b), c_(c), d_(d), e_(e) {}

private:
  int a_;
  int b_;
  int c_;
  int d_;
  int e_;
};

int main () {
  unsigned int const nOrbits = 1500;
  unsigned int const nBXsPerOrbit = 3564;
  unsigned int const nBXs = nOrbits * nBXsPerOrbit;

  std::string const delimiter = "================================================";
  unsigned int test_idx = 0;

  std::cout << delimiter << std::endl;
  std::cout << "nOrbits = " << nOrbits << ", nBXs = " << nBXs << std::endl;
  std::cout << delimiter << std::endl;

  // Number of CaloTowers for every BX.
  //  - Using here as rough approximation a Gaussian distribution,
  //    based on the CaloTowers' multiplicity observed in 2025 ZeroBias data.
  std::random_device rd;
  std::mt19937 gen(rd());
  std::normal_distribution distrib{1500., 600.};

  std::vector<int> nCaloTowers_vec{};
  nCaloTowers_vec.reserve(nBXs);
  for (auto ibx = 0u; ibx < nBXs; ++ibx) {
    nCaloTowers_vec.emplace_back(std::min(4095l, std::max(1l, std::lround(distrib(gen)))));
  }

  std::cout << "Generated " << nBXs << " random integers" << std::endl;
  std::cout << delimiter << std::endl;

  //
  // Test #1
  //
  ++test_idx;
  {
    auto startTime = std::chrono::steady_clock::now();

    std::vector<std::vector<Object>> orbitBuffer(nBXsPerOrbit + 1);
    for (auto& bxVec : orbitBuffer) {
      bxVec.reserve(4096);
    }

    for (auto ior = 0u; ior < nOrbits; ++ior) {
      for (auto ibx = 1u; ibx <= nBXsPerOrbit; ++ibx) {
        auto const nCaloTowers = nCaloTowers_vec.at((ibx - 1) + ior * nBXsPerOrbit);
        for (auto ict = 0; ict < nCaloTowers; ++ict) {
          orbitBuffer[ibx].emplace_back(1, 2, 3, 4, 5);
        }
      }

      for (auto& bxVec : orbitBuffer) {
        bxVec.clear();
      }
    }

    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration<double>(endTime - startTime);
    std::cout << "Test #" << test_idx << ": " << duration.count() << " sec" << std::endl;
    std::cout << delimiter << std::endl;
  }

  //
  // Test #2
  //
  ++test_idx;
  {
    auto startTime = std::chrono::steady_clock::now();

    std::vector<std::vector<Object>> orbitBuffer(nBXsPerOrbit + 1);

    for (auto ior = 0u; ior < nOrbits; ++ior) {
      for (auto ibx = 1u; ibx <= nBXsPerOrbit; ++ibx) {
        auto const nCaloTowers = nCaloTowers_vec.at((ibx - 1) + ior * nBXsPerOrbit);
        orbitBuffer[ibx].reserve(nCaloTowers);
        for (auto ict = 0; ict < nCaloTowers; ++ict) {
          orbitBuffer[ibx].emplace_back(1, 2, 3, 4, 5);
        }
      }

      for (auto& bxVec : orbitBuffer) {
        bxVec.clear();
      }
    }

    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration<double>(endTime - startTime);
    std::cout << "Test #" << test_idx << ": " << duration.count() << " sec" << std::endl;
    std::cout << delimiter << std::endl;
  }

  //
  // Test #3
  //
  ++test_idx;
  {
    auto startTime = std::chrono::steady_clock::now();

    for (auto ior = 0u; ior < nOrbits; ++ior) {
      std::vector<std::vector<Object>> orbitBuffer(nBXsPerOrbit + 1);
      for (auto ibx = 1u; ibx <= nBXsPerOrbit; ++ibx) {
        auto const nCaloTowers = nCaloTowers_vec.at((ibx - 1) + ior * nBXsPerOrbit);
        orbitBuffer[ibx].reserve(nCaloTowers);
        for (auto ict = 0; ict < nCaloTowers; ++ict) {
          orbitBuffer[ibx].emplace_back(1, 2, 3, 4, 5);
        }
      }

      for (auto& bxVec : orbitBuffer) {
        bxVec.clear();
      }
    }

    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration<double>(endTime - startTime);
    std::cout << "Test #" << test_idx << ": " << duration.count() << " sec" << std::endl;
    std::cout << delimiter << std::endl;
  }

  return 0;
}
