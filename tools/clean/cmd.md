# 预览：检查小于 50MB 的视频
python tools/clean/clean_small_videos.py "E:\av\av新"

# 删除：删除小于 50MB 的视频
python tools/clean/clean_small_videos.py "E:\av\av新" --delete

# 自定义阈值（例如 80MB）
python tools/clean/clean_small_videos.py "E:\av\av新" --threshold-mb 80
python tools/clean/clean_small_videos.py "E:\av\av新" --threshold-mb 80 --delete
