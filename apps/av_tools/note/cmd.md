# 1 只检查/启动 API
python -m apps.av_tools.run fetch-metadata --start-api-only --no-env-proxy

# 2 扫目录抓取元数据（多源 fallback: javdb -> javbus_api -> r18）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --request-interval 1.5 --no-env-proxy

python -m apps.av_tools.run fetch-metadata --codes-json "C:\Base1\my_program\codes.json" --no-env-proxy

# 指定 provider 顺序（命令行优先级高于 runtime.toml）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javdb,r18" --no-env-proxy
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javbus_browser,javdb,r18" --no-env-proxy

# 指定 provider 超时（秒，命令行优先级高于 runtime.toml）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javdb,r18" --provider-timeout 5 --no-env-proxy



# 仅走原有轻量链路（不启用 browser fallback）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode http --no-env-proxy

# 失败后再启用 browser fallback（推荐）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode browser-on-error --no-env-proxy

# 调试：始终优先 browser fallback
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode browser-always --no-env-proxy

# 用 javbus_api
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode api-only --request-interval 0 --no-env-proxy



# 只走浏览器并弹出窗口看过程
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode browser-only --show-browser --no-env-proxy

# 用 javdb,r18
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javdb,r18" --download-mode browser-on-error --provider-timeout 5 --request-interval 0.5





# 3 单文件
python -m apps.av_tools.run fetch-metadata --input "D:\videos\ABC-123.mp4" --no-env-proxy

# 4 指定输出目录
python -m apps.av_tools.run fetch-metadata --input "D:\videos" --output-dir "D:\reports" --no-env-proxy

# 5 只提取番号（不查 API）
python -m apps.av_tools.run extract-codes --input "E:\av\日本"
python -m apps.av_tools.run extract-codes --codes-json "E:\codes\source.json"

# 6 下载方式（命令行优先级高于 runtime.toml）
# 6.0 极速：仅本地 API（最接近旧版速度）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode api-only --no-env-proxy

# 6.1 仅 HTTP 解析（关闭 browser fallback）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode http --no-env-proxy

# 6.2 全部失败后再启用 browser fallback（推荐）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode browser-on-error --no-env-proxy

# 6.3 始终优先 browser fallback（调试）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --download-mode browser-always --no-env-proxy
