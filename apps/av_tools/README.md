# av_tools

统一 Python AV 工具入口，当前包含：

- `index-formatter`：标准化视频文件名中的番号格式。
- `move-by-actor`：按番号查询演员并搬运视频到演员目录。
- `fetch-metadata`：递归提取番号并查询标题、演员、封面 URL，输出 JSON/CSV 报告。
- `extract-codes`：仅提取标准番号（不调 API），输出 JSON，便于后续解析。

## 统一入口

```bash
python -m apps.av_tools.run <subcommand> [args...]
```

## 子命令

### index-formatter

```bash
# 预览
python -m apps.av_tools.run index-formatter "E:\\av\\日本"

# 应用改名
python -m apps.av_tools.run index-formatter "E:\\av\\日本" --apply
```

### move-by-actor

```bash
# 预览搬运
python -m apps.av_tools.run move-by-actor --input "D:\\videos"

# 真实搬运
python -m apps.av_tools.run move-by-actor --input "D:\\videos" --apply
```

### fetch-metadata

```bash
# 递归扫描目录并输出报告到默认目录 out/av_tools/fetch_metadata
python -m apps.av_tools.run fetch-metadata --input "D:\\videos"

# 单文件查询并指定输出目录
python -m apps.av_tools.run fetch-metadata --input "D:\\videos\\ABC-123.mp4" --output-dir "D:\\reports"

# 命令行覆盖下载模式（优先级高于 runtime.toml）
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --download-mode http

# 极速模式：只走本地 javbus_api（最接近旧版速度）
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --download-mode api-only

# 命令行覆盖 provider 顺序（优先级高于 runtime.toml）
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --providers "javbus_browser,javdb,r18"

# 命令行覆盖 provider 超时（秒，优先级高于 runtime.toml）
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --providers "javdb,r18" --provider-timeout 5

# 只走浏览器抓取（Playwright）
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --download-mode browser-only

# 只走浏览器抓取并弹出浏览器窗口观察过程
python -m apps.av_tools.run fetch-metadata --input "D:\\videos" --download-mode browser-only --show-browser
```

`fetch-metadata` 会实时写入 `result.csv` / `failed.csv`，并在终端显示 `tqdm` 进度条（固定显示最近 3 个成功番号）。
`fetch-metadata` 采用多源 Provider fallback（默认顺序：`javdb -> javbus_api -> r18`）。

可在 `apps/av_tools/move_by_actor/runtime.toml` 调整 Provider 顺序与站点地址，例如：

```toml
[providers]
enabled = ["javdb", "javbus_api", "r18"]

[providers.network]
timeout_sec = 20
request_interval_sec = 1.0

[providers.javdb]
enabled = true
base_url = "https://javdb8.com/"

[providers.javbus_browser]
enabled = false
base_url = "https://www.javbus.com/"
headless = true
nav_timeout_sec = 15

[providers.browser_fallback]
mode = "off" # off | on_error | always | only
headless = true
nav_timeout_sec = 15
```

当启用 browser fallback（`mode=on_error/always`）时，需要先安装：

```bash
pip install playwright beautifulsoup4
python -m playwright install chromium
```

### extract-codes

```bash
# from directory or single file path
python -m apps.av_tools.run extract-codes --input "D:\\videos"

# from a JSON source (e.g. {"codes": ["IPSD-048-A", "abc123"]})
python -m apps.av_tools.run extract-codes --codes-json "D:\\codes\\source.json"
```

默认输出路径为 `out/av_tools/extract_codes/codes.json`。
