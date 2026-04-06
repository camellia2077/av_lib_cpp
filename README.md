# av_lib_cpp
查询av是否下载过，看过

## 文件夹层级
```
apps/                      # 应用入口与表现层
├── cli/
└── gui/
src/                       # 核心业务实现
└── core/
    ├── app/               # 应用服务与用例编排
    ├── data/              # 数据查询与仓储实现
    ├── infrastructure/    # 外部基础设施（数据库等）
    ├── io/                # 文件读取等 I/O
    ├── ports/             # 核心依赖的抽象接口
    └── utils/             # 核心通用工具
third_party/               # 第三方依赖
└── imgui/
tools/
└── script/
tests/
cmake/
CMakeLists.txt
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
python tools/script/run.py build --mode release
```

快速调试构建：

```bash
python tools/script/run.py build --mode fast
```

执行 clang-tidy：

```bash
python tools/script/run.py build --mode tidy
```

运行 C++ 核心测试：

```bash
python tools/script/run.py test-core
```

运行 Python 端到端（CLI）冒烟测试：

```bash
python tools/script/run.py smoke-cli
```

## Python AV 工具入口

统一入口：

```bash
python -m apps.av_tools.run <subcommand> [args...]
```

常用子命令：

```bash
python -m apps.av_tools.run index-formatter "E:\\av\\日本"
python -m apps.av_tools.run move-by-actor --input "D:\\videos"
python -m apps.av_tools.run fetch-metadata --input "D:\\videos"
```
