# recursive directory scan
python -m apps.av_tools.run fetch-metadata --input "E:\av\done"

# single file scan
python -m apps.av_tools.run fetch-metadata --input "E:\av\done\ABC-123.mp4"

# custom output directory
python -m apps.av_tools.run fetch-metadata --input "E:\av\done" --output-dir "E:\av\report"

# start api only
python -m apps.av_tools.run fetch-metadata --start-api-only

