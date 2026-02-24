# av_lib_cpp
查询av是否下载过，看过

## 文件夹层级
```
src/
├── main.cpp
├── cmd_main.cpp
├── common/
├── core/
│   ├── app/               # 应用服务与用例编排
│   ├── data/              # 数据查询与仓储实现
│   ├── infrastructure/    # 外部基础设施（数据库等）
│   ├── io/                # 文件读取等 I/O
│   ├── ports/             # 核心依赖的抽象接口
│   └── utils/             # 核心通用工具
└── presentation/
    ├── cli/               # 命令行表现层
    │   ├── input_parser.hpp
    │   ├── framework/
    │   └── impl/
    └── gui/               # 图形界面表现层
        ├── i_gui_view.hpp
        ├── framework/
        └── imgui/         # GUI 表现层
```

## 第三方库 (Third-Party Libraries)

本项目使用了以下第三方库：

### [Dear ImGui](https://github.com/ocornut/imgui)

- **简介**: 一个无膨胀、快速、可移植的 C++ 图形用户界面库。
- **版权**: Copyright (c) 2014-2024 Omar Cornut
- **许可证**: [MIT License](https://github.com/ocornut/imgui/blob/master/LICENSE.txt)

感谢其为本项目提供了强大的图形界面支持。

## 静态链接构建

默认启用静态链接（`AVLIB_STATIC_LINK=ON`），可用以下命令构建：

```bash
cmake -S . -B build -DAVLIB_STATIC_LINK=ON
cmake --build build -j 8
```

如果要切回动态链接：

```bash
cmake -S . -B build -DAVLIB_STATIC_LINK=OFF
cmake --build build -j 8
```
