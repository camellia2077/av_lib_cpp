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