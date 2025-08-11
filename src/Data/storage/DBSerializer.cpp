#include "DBSerializer.h"
#include <fstream>
#include <iostream>
#include <cstdio> // For std::rename, std::remove

/**
 * @brief 从二进制文件中加载ID集合。
 * * 该函数以二进制模式读取指定的文件，并按照 "长度前缀 + 数据" 的格式
 * 解析出每一个ID字符串，然后将它们存入一个无序集合中返回。
 * * @param filepath 数据库文件的路径。
 * @return std::unordered_set<std::string> 包含所有已加载ID的集合。如果文件不存在，则返回一个空集合。
 */
std::unordered_set<std::string> DBSerializer::load(const std::string& filepath) {
    // 创建一个空的字符串集合，用于存放从文件中读取的ID。
    std::unordered_set<std::string> id_set;
    
    // 以二进制输入模式(`std::ios::binary`)打开文件。
    // 二进制模式可确保在不同操作系统上都能正确处理数据，不会发生换行符转换等问题。
    std::ifstream infile(filepath, std::ios::binary);
    
    // 检查文件是否成功打开。如果文件不存在或无法打开，!infile会返回true。
    // 在本应用中，首次运行时文件不存在是正常情况，直接返回空集合即可。
    if (!infile) {
        return id_set;
    }

    // 循环读取文件，直到文件末尾或发生错误。
    // `while(infile)` 会检查流的状态，只要不是eofbit或badbit，就会继续循环。
    while (infile) {
        // 定义一个32位无符号整数，用于存储即将读取的字符串的长度。
        uint32_t len;
        
        // 从文件中读取长度信息。
        // reinterpret_cast<char*>(&len) 将`len`变量的地址转换为`char*`指针，
        // `sizeof(len)` 指定了要读取的字节数（对于uint32_t通常是4字节）。
        // 这会直接从文件中读取4个字节并填充到len变量中。
        infile.read(reinterpret_cast<char*>(&len), sizeof(len));
        
        // 在读取长度后，立即检查是否到达了文件末尾。
        // 这是一种常见的处理方式，因为最后一次成功的读取可能恰好读完文件，
        // 此时eof标志位会被设置，下一轮循环的`while(infile)`会失败。
        // 如果在读取长度时就到达了文件末尾，则直接跳出循环。
        if (infile.eof()) break;

        // 根据刚刚读取到的长度`len`，创建一个相应大小并用空字符('\0')初始化的字符串。
        // 预分配内存可以提高效率。
        std::string id(len, '\0');
        
        // 从文件中读取实际的字符串数据，长度为`len`。
        // `&id[0]` 获取字符串内部缓冲区的首地址。
        infile.read(&id[0], len);
        
        // 检查上一步的读取操作是否成功。
        // `infile.good()` 确保流没有发生任何错误（如IO错误或逻辑错误）。
        // 如果读取成功，则将这个ID插入到集合中。
        if (infile.good()) {
            id_set.insert(id);
        }
    }
    
    // 读取完成后，在控制台输出一条日志，告知用户加载完成及记录总数。
    std::cout << "数据库 " << filepath << " 加载完成，共 " << id_set.size() << " 条记录。" << std::endl;
    
    // 返回包含所有ID的集合。
    return id_set;
}

/**
 * @brief 将ID集合以二进制格式保存到文件。
 *
 * 该函数采用“原子写入”策略来保证数据安全：
 * 1. 将所有数据写入一个临时文件（例如 `database.bin.tmp`）。
 * 2. 如果写入成功，则删除旧的正式文件。
 * 3. 将临时文件重命名为正式文件名。
 * 这样做可以防止因程序中途崩溃或磁盘空间不足而导致原数据文件损坏或丢失。
 *
 * @param filepath 目标数据库文件的路径。
 * @param id_set 包含所有需要保存的ID的集合。
 * @return bool 如果保存成功则返回true，否则返回false。
 */
bool DBSerializer::save(const std::string& filepath, const std::unordered_set<std::string>& id_set) {
    // 构造临时文件的路径，在原文件名后加上".tmp"。
    std::string tmp_filepath = filepath + ".tmp";
    
    // 创建并打开一个输出文件流，使用二进制模式(`std::ios::binary`)和截断模式(`std::ios::trunc`)。
    // `trunc`模式会清空任何已存在的同名文件内容。
    std::ofstream outfile(tmp_filepath, std::ios::binary | std::ios::trunc);

    // 检查临时文件是否成功创建。如果失败（如因权限问题），则输出错误信息并返回false。
    if (!outfile) {
        std::cerr << "错误：无法创建临时数据库文件 " << tmp_filepath << std::endl;
        return false;
    }

    // 遍历集合中的每一个ID字符串。
    for (const auto& id : id_set) {
        // 获取当前ID字符串的长度（字节数）。
        uint32_t len = id.length();
        
        // 将长度（一个32位整数）写入文件。
        // `reinterpret_cast<const char*>` 用于将变量地址转换为字节流指针。
        outfile.write(reinterpret_cast<const char*>(&len), sizeof(len));
        
        // 接着将字符串的实际内容（原始字节）写入文件。
        // `id.c_str()` 返回一个指向字符串内容的const char*指针。
        outfile.write(id.c_str(), len);
    }
    
    // 完成所有写入后，关闭文件流。关闭操作会将所有缓冲区中的数据刷入磁盘。
    outfile.close();
    
    // 检查关闭后的文件流状态。如果`good()`返回false，说明在写入或关闭过程中发生了错误。
    if (!outfile.good()) {
        std::cerr << "错误：写入临时文件失败。" << std::endl;
        return false;
    }

    // --- 原子替换操作 ---
    // 1. 删除旧的正式数据库文件。如果文件不存在，`remove`不会报错。
    std::remove(filepath.c_str());
    
    // 2. 将新写入的临时文件重命名为正式文件名。
    // `std::rename`是一个原子或接近原子的操作（在多数文件系统上）。
    // 如果重命名失败（例如，其他程序正在占用旧文件），它会返回一个非零值。
    if (std::rename(tmp_filepath.c_str(), filepath.c_str()) != 0) {
        std::cerr << "错误：无法将临时文件重命名为正式文件。" << std::endl;
        // 如果重命名失败，为保持清洁，尝试删除已创建的临时文件。
        std::remove(tmp_filepath.c_str());
        return false;
    }
    
    // 所有操作成功完成。
    return true;
}