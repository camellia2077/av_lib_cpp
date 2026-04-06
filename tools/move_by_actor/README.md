# move_by_actor

## 目标

将“按番号查演员并搬运视频”流程拆分为清晰模块，避免单文件过重，方便后续维护和扩展。

## 模块拆分

- `run.py`
  - 对外统一入口脚本，直接复制命令即可使用。

- `av-spider.py`
  - 兼容旧命令的入口包装器（内部转发到 `app.cli`）。

- `app/cli.py`
  - 命令行参数解析与主流程编排。
  - 处理输入目录、目标目录、配置构建和汇总输出。

- `app/config.py`
  - 运行配置数据结构（API 地址、超时、代理开关）。
  - 包含运行时 API 启动选项结构体。

- `app/models.py`
  - 领域模型定义（如 `MovieInfo`）。

- `app/api_client.py`
  - 与 API 交互，负责按番号查询影片信息并提取演员列表。

- `app/scanner.py`
  - 文件扫描与番号提取逻辑。
  - 包含视频扩展名过滤与 `stem -> code` 提取规则。

- `app/file_ops.py`
  - 文件系统辅助逻辑。
  - 包含演员目录名清洗、目标重名处理。

- `app/service.py`
  - 核心业务流程：扫描 -> 查演员 -> 决策是否搬运 -> 执行搬运。
  - Ctrl+C 中断安全退出。

- `app/runtime_config.py`
  - 读取 `runtime.toml` 并转换为运行时启动配置。

- `app/api_runtime.py`
  - API 健康检查与可选自动启动逻辑。

- `runtime.toml`
  - 运行时配置文件（API 项目目录、启动命令、健康检查、自动启动策略）。

## 颜色输出规则

- 预览模式（默认，不加 `--apply`）：
  - 输出保持默认字体颜色（不着色）。

- 执行模式（加 `--apply`）：
  - 实际 `[MOVE]` 行使用绿色 ANSI 颜色输出。

## 递归搬运规则

- 当使用 `--recursive` 时：
  - 若某个子目录包含视频文件，则该子目录会作为一个整体搬运单位（`[MOVE][DIR]`）。
  - 番号优先从目录名提取；如果目录名提取不到，再尝试该目录内视频文件名。
  - 这样可以把 `PRST-004` / `MIZD-374` 这种“每个番号一个文件夹”的结构整体移动到演员目录。

- 不使用 `--recursive` 时：
  - 仍按单个视频文件作为搬运单位（`[MOVE][FILE]`）。

## 用法

```bash
# 预览（不移动）
python tools/move_by_actor/run.py --input "D:\\videos"

# 执行移动（[MOVE] 行显示绿色）
python tools/move_by_actor/run.py --input "D:\\videos" --apply

# 递归扫描 + 指定输出根目录
python tools/move_by_actor/run.py --input "D:\\videos" --recursive --output "D:\\actors"

# 禁用环境代理
python tools/move_by_actor/run.py --input "D:\\videos" --no-env-proxy

# 当 API 未启动时自动拉起（可覆盖 runtime.toml）
python tools/move_by_actor/run.py --input "D:\\videos" --auto-start-api

# 若本次自动拉起了 API，任务结束后自动关闭它
python tools/move_by_actor/run.py --input "D:\\videos" --auto-start-api --stop-api-on-exit

# 只启动/检查 API（不执行扫描和搬运）
python tools/move_by_actor/run.py --start-api-only
```

## runtime.toml

默认路径：`tools/move_by_actor/runtime.toml`

```toml
[api]
auto_start = false
project_dir = "C:\\code\\javbus-api"
start_command = "npm start"
healthcheck_url = "http://127.0.0.1:3000/"
startup_timeout_sec = 60
poll_interval_sec = 1.0
stop_on_exit = false
```
