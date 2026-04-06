# av_lib_cpp
查询av是否下载过，看过

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

## 设计参考

`apps/av_tools` 的多源元数据抓取与 Provider 抽象思路，参考了
[`JavScraper/Emby.Plugins.JavScraper`](https://github.com/JavScraper/Emby.Plugins.JavScraper)
在数据源编排、字段归一化和扩展性方面的实践。

当前仓库为独立实现，按本项目需求使用 Python 架构与模块边界组织代码，
并未直接复用该仓库的插件代码。
