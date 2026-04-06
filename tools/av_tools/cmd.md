# Debug Web Fetch

通过命令行抓取网页 HTML，并输出解析后的 JSON 报告（候选、精确命中、风控标记）。

## 示例

```bash
# 测试 javdb571 + BOKD-250（requests + browser）
python tools/av_tools/debug_web_fetch.py --site custom --base-url "https://javdb571.com/search?q={code}&f=all" --code BOKD-250 --mode both

# 仅浏览器抓取并弹窗观察过程
python tools/av_tools/debug_web_fetch.py --site custom --base-url "https://javdb571.com/search?q={code}&f=all" --code BOKD-250 --mode browser --show-browser
```

输出：

* HTML 文件：`temp/probe_output/<site>_<code>_<mode>_<timestamp>.html`
* JSON 报告：`temp/probe_output/<site>_<code>_report_<timestamp>.json`
