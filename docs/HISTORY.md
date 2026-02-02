## v0.2.1 - 2026-02-01

### 技术改进/重构 (Changed/Refactor)
* 全面同步代码命名规范，将所有核心模块的方法名从 `snake_case` 重构为 `PascalCase`（例如：`perform_add` → `PerformAdd`, `init` → `Init`）。
* 同步枚举与常量命名，统一使用 `kPascalCase` 格式（符合 C++23 风格指南，例如：`ErrorCode::DBNotExist` → `ErrorCode::kDbNotExist`）。
* 对 **Application**、**DatabaseManager**、**FastQueryDB**、**Validator**、**ThemeManager** 等核心类进行结构化重构以支持新命名规范。

### 修复 (Fixed)
* 修复 **FastQueryDB** 因缺少虚析构函数导致的 `vtable` 链接错误。
* 修复 **ImGuiView** 虚函数签名与 `IGuiView` 接口不匹配导致的抽象类实例化失败。
* 纠正 `main.cpp` 与 `cmd_main.cpp` 中的入口调用逻辑。

### 新增功能 (Added)
* 在 **IIdRepository** 接口及 **FastQueryDB** 实现中新增事务控制支持：`BeginTransaction`、`CommitTransaction`、`RollbackTransaction`。


1. 新增 clang-tidy 脚本
2. 新增 clang-format 脚本





## v0.1.1 - 2025-10-16
1. 新增版本信息
2. 字母部分长度至少为1,数字部分长度至少为1
3. cmake编译脚本放入src/script内
4. 优化ImGui内代码结构


## v0.1.0 - 2025-10-10
1. 新增注释
2. .h后缀修改为.hpp






