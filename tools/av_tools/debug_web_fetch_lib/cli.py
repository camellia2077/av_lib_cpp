from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import asdict
from pathlib import Path

from .fetchers import fetch_browser, fetch_requests
from .models import DEFAULT_BASE_URLS, ParseSiteName, ProbeMode, SiteName
from .parsers import parse_candidates
from .utils import (
    build_url,
    detect_block_markers,
    infer_parse_site,
    normalize_code,
    save_html,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch search HTML and parse candidates into JSON for AV site debugging."
    )
    parser.add_argument("--site", choices=["javdb", "javbus", "r18", "custom"], required=True)
    parser.add_argument("--code", required=True, help="Movie code, e.g. BOKD-250")
    parser.add_argument("--mode", choices=["requests", "browser", "both"], default="both")
    parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "Base URL override. For --site custom, pass a full template with {code}, "
            "e.g. https://javdb571.com/search?q={code}&f=all"
        ),
    )
    parser.add_argument("--timeout", type=float, default=12.0, help="Request timeout seconds")
    parser.add_argument("--show-browser", action="store_true", help="Show browser window in browser mode")
    parser.add_argument("--no-env-proxy", action="store_true", help="Disable env proxy in requests mode")
    parser.add_argument("--output-dir", default="temp/probe_output", help="Output directory for html/json")
    parser.add_argument(
        "--parse-as",
        choices=["javdb", "javbus", "r18", "none"],
        default=None,
        help="Parsing rule set. Default auto-infer for custom site.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional output json path; default is generated under output-dir",
    )
    return parser.parse_args()


def run_mode(
    *,
    site: SiteName,
    parse_site: ParseSiteName,
    mode_name: str,
    code: str,
    url: str,
    base_url: str,
    timeout: float,
    output_dir: Path,
    use_env_proxy: bool,
    show_browser: bool,
) -> dict[str, object]:
    if mode_name == "requests":
        status, html, final_url, title = fetch_requests(url, timeout, use_env_proxy)
    else:
        status, html, final_url, title = fetch_browser(url, timeout, show_browser)

    html_path = save_html(output_dir, f"{site}_{code}_{mode_name}", html)
    candidates = parse_candidates(parse_site, html, base_url)
    exact = [
        asdict(item)
        for item in candidates
        if normalize_code(item.code) == normalize_code(code)
    ]

    return {
        "mode": mode_name,
        "status": status,
        "final_url": final_url,
        "title": title,
        "html_path": str(html_path),
        "html_bytes": len(html.encode("utf-8", errors="ignore")),
        "blocked_markers": detect_block_markers(html, title, status),
        "candidate_count": len(candidates),
        "exact_match_count": len(exact),
        "exact_matches": exact,
        "candidates_preview": [asdict(item) for item in candidates[:10]],
    }


def main() -> None:
    args = parse_args()
    site: SiteName = args.site
    code = normalize_code(args.code) or args.code.strip().upper()
    if not code:
        raise SystemExit("Invalid --code")

    base_url = (args.base_url or DEFAULT_BASE_URLS.get(site) or "").strip()
    if not base_url:
        raise SystemExit("Missing base URL. Provide --base-url.")

    url = build_url(site, code, base_url)
    output_dir = Path(args.output_dir).expanduser().resolve()
    mode: ProbeMode = args.mode
    parse_site = infer_parse_site(site, base_url, args.parse_as)

    print(f"[RUN] site={site}")
    print(f"[RUN] code={code}")
    print(f"[RUN] mode={mode}")
    print(f"[RUN] url={url}")
    print(f"[RUN] parse_as={parse_site}")
    print(f"[RUN] output_dir={output_dir}")

    runs: list[dict[str, object]] = []
    modes = ["requests", "browser"] if mode == "both" else [mode]
    for mode_name in modes:
        print(f"[{mode_name.upper()}] start")
        try:
            run = run_mode(
                site=site,
                parse_site=parse_site,
                mode_name=mode_name,
                code=code,
                url=url,
                base_url=base_url,
                timeout=float(args.timeout),
                output_dir=output_dir,
                use_env_proxy=not args.no_env_proxy,
                show_browser=bool(args.show_browser),
            )
            runs.append(run)
            print(
                f"[{mode_name.upper()}] status={run['status']} "
                f"title={run['title'] or '(empty)'} exact={run['exact_match_count']}"
            )
            print(f"[{mode_name.upper()}] html={run['html_path']}")
        except Exception as exc:
            runs.append({"mode": mode_name, "error": str(exc)})
            print(f"[{mode_name.upper()}][ERROR] {exc}")

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "site": site,
        "code": code,
        "search_url": url,
        "base_url": base_url,
        "parse_as": parse_site,
        "runs": runs,
    }

    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
    else:
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_json = output_dir / f"{site}_{code}_report_{timestamp}.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OUTPUT] report_json={output_json}")
