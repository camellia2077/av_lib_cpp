# 开启api 
python -m apps.av_tools.run move-by-actor --start-api-only


# 只启动/检查 API（不扫描、不搬运）
python -m apps.av_tools.run move-by-actor --start-api-only

# 预览（只看结果，不移动）
python -m apps.av_tools.run move-by-actor --input "E:\av\done" --no-env-proxy

# 真正执行搬运
python -m apps.av_tools.run move-by-actor --input "E:\av\done" --apply --no-env-proxy

# 递归扫描 + 指定目标根目录
python -m apps.av_tools.run move-by-actor --input "E:\av\done\a" --recursive --output "E:\av\done" --no-env-proxy

# 递归扫描 + 指定目标根目录 + 搬运
python -m apps.av_tools.run move-by-actor --input "E:\av\done\a" --recursive --output "E:\av\done" --no-env-proxy --apply

# 如果不想走环境代理
python -m apps.av_tools.run move-by-actor --input "D:\你的视频目录" --no-env-proxy


python -m apps.av_tools.run move-by-actor --input "E:\av\木桶饭" --recursive --output "E:\av\done" --no-env-proxy --apply --auto-start-api
