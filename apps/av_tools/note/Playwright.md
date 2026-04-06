# 只走浏览器（Playwright）显示
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javbus_browser" --download-mode http --provider-timeout 8 --request-interval 0 --show-browser --no-env-proxy

# 只走浏览器（Playwright）不显示
python -m apps.av_tools.run fetch-metadata --input "E:\av\日本" --providers "javbus_browser" --download-mode http --provider-timeout 8 --request-interval 0.5 --no-env-proxy
