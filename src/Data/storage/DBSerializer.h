#pragma once

#include <string>
#include <unordered_set>

// 负责将ID集合与文件进行序列化和反序列化
class DBSerializer {
public:
    // 从文件加载数据，返回一个ID集合
    static std::unordered_set<std::string> load(const std::string& filepath);

    // 将一个ID集合保存到文件
    static bool save(const std::string& filepath, const std::unordered_set<std::string>& id_set);
};