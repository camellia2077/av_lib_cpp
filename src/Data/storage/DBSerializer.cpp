#include "DBSerializer.h"
#include <fstream>
#include <iostream>
#include <cstdio> // For std::rename, std::remove

std::unordered_set<std::string> DBSerializer::load(const std::string& filepath) {
    std::unordered_set<std::string> id_set;
    std::ifstream infile(filepath, std::ios::binary);
    if (!infile) {
        // 文件不存在是正常情况
        return id_set;
    }

    while (infile) {
        uint32_t len;
        infile.read(reinterpret_cast<char*>(&len), sizeof(len));
        if (infile.eof()) break;

        std::string id(len, '\0');
        infile.read(&id[0], len);
        
        if (infile.good()) {
            id_set.insert(id);
        }
    }
    std::cout << "数据库 " << filepath << " 加载完成，共 " << id_set.size() << " 条记录。" << std::endl;
    return id_set;
}

bool DBSerializer::save(const std::string& filepath, const std::unordered_set<std::string>& id_set) {
    std::string tmp_filepath = filepath + ".tmp";
    std::ofstream outfile(tmp_filepath, std::ios::binary | std::ios::trunc);

    if (!outfile) {
        std::cerr << "错误：无法创建临时数据库文件 " << tmp_filepath << std::endl;
        return false;
    }

    for (const auto& id : id_set) {
        uint32_t len = id.length();
        outfile.write(reinterpret_cast<const char*>(&len), sizeof(len));
        outfile.write(id.c_str(), len);
    }
    
    outfile.close();
    if (!outfile.good()) {
        std::cerr << "错误：写入临时文件失败。" << std::endl;
        return false;
    }

    std::remove(filepath.c_str());
    if (std::rename(tmp_filepath.c_str(), filepath.c_str()) != 0) {
        std::cerr << "错误：无法将临时文件重命名为正式文件。" << std::endl;
        std::remove(tmp_filepath.c_str());
        return false;
    }
    
    return true;
}