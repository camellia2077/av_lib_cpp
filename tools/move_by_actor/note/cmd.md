# 开启api 
python tools/move_by_actor/run.py --start-api-only


# 只启动/检查 API（不扫描、不搬运）
python tools/move_by_actor/run.py --start-api-only

# 预览（只看结果，不移动）
python tools/move_by_actor/run.py --input "E:\av\done" --no-env-proxy

# 真正执行搬运
python tools/move_by_actor/run.py --input "E:\av\done" --apply --no-env-proxy

# 递归扫描 + 指定目标根目录
python tools/move_by_actor/run.py --input "E:\av\done\a" --recursive --output "E:\av\done" --no-env-proxy

# 递归扫描 + 指定目标根目录 + 搬运
python tools/move_by_actor/run.py --input "E:\av\done\a" --recursive --output "E:\av\done" --no-env-proxy --apply

# 如果不想走环境代理
python tools/move_by_actor/run.py --input "D:\你的视频目录" --no-env-proxy


python tools/move_by_actor/run.py --input "E:\av\木桶饭" --recursive --output "E:\av\done" --no-env-proxy --apply --auto-start-api
