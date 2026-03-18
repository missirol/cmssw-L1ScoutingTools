#include <array>
#include <cassert>
#include <chrono>
#include <iostream>
#include <vector>

class Object {
public:
  Object(int val) {
    val0_ = val;
    val1_ = val;
    val2_ = val;
    val3_ = val;
    val4_ = val;
  }
private:
  int val0_;
  int val1_;
  int val2_;
  int val3_;
  int val4_;
};

template<class ObjType>
class OrbitCollection1 {
public:
  OrbitCollection1() {}

  size_t size() const { return data_.size(); }

  void fill(std::vector<std::vector<ObjType>>& arr) {
    size_t size{0};
    for (auto const& subarr : arr) {
      size += subarr.size();
    }

    data_.clear();
    data_.reserve(size);

    for (auto& bxVec : arr) {
      if (bxVec.size() > 0) {
        data_.insert(data_.end(), bxVec.begin(), bxVec.end());
        bxVec.clear();
      }
    }
  }
private:
  std::vector<ObjType> data_;
};

template<class ObjType>
class OrbitCollection2 {
public:
  OrbitCollection2() {}

  static constexpr unsigned int kBxArraySize = 3565;

  using BxArray = std::array<std::vector<ObjType>, kBxArraySize>;

  size_t size() const { return data_.size(); }

  void fill(BxArray const& arr) {
    size_t size{0};
    for (auto const& subarr : arr) {
      size += subarr.size();
    }

    data_.clear();
    data_.reserve(size);

    for (auto const& subarr : arr) {
      if (not subarr.empty()) {
        data_.insert(data_.end(), subarr.begin(), subarr.end());
      }
    }
  }
private:
  std::vector<ObjType> data_;
};

int main() {

  using ObjectOrbitCollection2 = OrbitCollection2<Object>;

  unsigned int constexpr nEvents = 1000;
  unsigned int constexpr nObjectsPerBx = 200;

  size_t constexpr expected_size = ObjectOrbitCollection2::kBxArraySize * nObjectsPerBx;

  unsigned int test_idx = 0;
  std::string const delimiter = "================================================";
  std::cout << delimiter << std::endl;

  {
    auto startTime = std::chrono::steady_clock::now();
    for (auto ev = 0u; ev < nEvents; ++ev) {

      std::vector<std::vector<Object>> vec(ObjectOrbitCollection2::kBxArraySize);

      for (auto idx = 0u; idx < vec.size(); ++idx) {
        vec[idx].reserve(nObjectsPerBx);
        for (auto val = 0u; val < nObjectsPerBx; ++val) {
          vec[idx].emplace_back(val);
        }
      }

      OrbitCollection1<Object> oc1;
      oc1.fill(vec);

      assert(oc1.size() == expected_size);
    }

    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration<double>(endTime - startTime);
    std::cout << "Test #" << test_idx << ": " << duration.count() << " sec" << std::endl;
    std::cout << delimiter << std::endl;

    ++test_idx;
  }

  {
    auto startTime = std::chrono::steady_clock::now();
    for (auto ev = 0u; ev < nEvents; ++ev) {

      ObjectOrbitCollection2::BxArray arr;

      for (auto idx = 0u; idx < arr.size(); ++idx) {
        arr[idx].reserve(nObjectsPerBx);
        for (auto val = 0u; val < nObjectsPerBx; ++val) {
          arr[idx].emplace_back(val);
        }
      }

      ObjectOrbitCollection2 oc2;
      oc2.fill(arr);

      assert(oc2.size() == expected_size);
    }

    auto endTime = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration<double>(endTime - startTime);
    std::cout << "Test #" << test_idx << ": " << duration.count() << " sec" << std::endl;
    std::cout << delimiter << std::endl;

    ++test_idx;
  }

  return 0;
}
