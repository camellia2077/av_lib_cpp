
以下命令是根据番号，通过api，输出csv
推荐不开启全局，如果开启全局需要--no-env-proxy
仅启动/检查 API：
python -m apps.av_tools.run fetch-metadata --start-api-only

递归目录：
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --request-interval 1.5
 --no-env-proxy
单文件：
python -m apps.av_tools.run fetch-metadata --input "D:\videos\ABC-123.mp4"
指定输出目录：
python -m apps.av_tools.run fetch-metadata --input "D:\videos" --output-dir "D:\reports"




从目录/文件提取：
python -m apps.av_tools.run extract-codes --input "E:\av\日本"
从 JSON 提取：
python -m apps.av_tools.run extract-codes --codes-json "E:\codes\source.json"
自定义输出：
python -m apps.av_tools.run extract-codes --input "E:\av\日本" --output "C:\Computer\my_github\github


# 递归目录（禁用环境代理）
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --no-env-proxy

# 单文件（禁用环境代理）
python -m apps.av_tools.run fetch-metadata --input "D:\videos\ABC-123.mp4" --no-env-proxy

# 指定输出目录（禁用环境代理）
python -m apps.av_tools.run fetch-metadata --input "D:\videos" --output-dir "D:\reports" --no-env-proxy

# 仅启动/检查 API
python -m apps.av_tools.run fetch-metadata --start-api-only --no-env-proxy
