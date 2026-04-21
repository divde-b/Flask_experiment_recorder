#include <pybind11/pybind11.h>
#include <string>
#include <vector>
#include <algorithm>

namespace py = pybind11;

// 计算两个字符串的 Levenshtein 编辑距离
int levenshtein(const std::string& s1, const std::string& s2) {
    const size_t m = s1.size();
    const size_t n = s2.size();
    std::vector<size_t> dp(n + 1);
    for (size_t j = 0; j <= n; ++j) dp[j] = j;
    for (size_t i = 1; i <= m; ++i) {
        size_t prev = i;
        for (size_t j = 1; j <= n; ++j) {
            size_t cur = std::min({
                dp[j] + 1,
                prev + 1,
                dp[j-1] + (s1[i-1] == s2[j-1] ? 0 : 1)
            });
            dp[j-1] = prev;
            prev = cur;
        }
        dp[n] = prev;
    }
    return dp[n];
}

// 计算相似度（0~1，1表示完全相同）
double similarity(const std::string& s1, const std::string& s2) {
    if (s1.empty() && s2.empty()) return 1.0;
    int dist = levenshtein(s1, s2);
    int maxLen = std::max(s1.size(), s2.size());
    return 1.0 - static_cast<double>(dist) / maxLen;
}

// 模块导出
PYBIND11_MODULE(sim_metrics, m) {
    m.doc() = "字符串相似度计算模块（C++ 扩展）";
    m.def("levenshtein", &levenshtein, "计算编辑距离");
    m.def("similarity", &similarity, "计算相似度 (0~1)");
}