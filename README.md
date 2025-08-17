# av_lib_cpp
查询av是否下载过，看过

## 文件夹层级
```
├── App
│   ├── Application.cpp
│   ├── Application.h
│   ├── DatabaseManager.cpp
│   └── DatabaseManager.h
├── cmd_main.cpp
├── common
│   ├── cmd_pch.h
│   ├── MessageFormatter.cpp
│   ├── MessageFormatter.h
│   └── pch.h
├── Data/
│   ├── FastQueryDB.cpp # Facade封装
│   ├── FastQueryDB.h
│   ├── repository/
│   │   ├── IDRepository.cpp # 数据查询
│   │   └── IDRepository.h
│   └── storage/
│       ├── DBSerializer.cpp # 数据存储
│       └── DBSerializer.h
├── main.cpp
├── Utils
│   ├── Validator.cpp #输入内容验证
│   └── Validator.h
└── View
    ├── IGuiView.h
    └── ImGui
        ├── ImGuiView.cpp
        ├── ImGuiView.h
        └── UIConfig.h
```

## 第三方库 (Third-Party Libraries)

本项目使用了以下第三方库：

### [Dear ImGui](https://github.com/ocornut/imgui)

- **简介**: 一个无膨胀、快速、可移植的 C++ 图形用户界面库。
- **版权**: Copyright (c) 2014-2024 Omar Cornut
- **许可证**: [MIT License](https://github.com/ocornut/imgui/blob/master/LICENSE.txt)

感谢其为本项目提供了强大的图形界面支持。