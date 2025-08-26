import json
import datetime as dt
import requests


def format_duration(seconds):
    """将秒数格式化为 hh:mm:ss"""
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return "00:00:00"
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h:02d}:{m:02d}:{sec:02d}"


def format_pubdate(ts):
    """将时间戳格式化为 yyyy-mm-dd hh:mm:ss（本地时区）"""
    try:
        t = int(ts)
    except (TypeError, ValueError):
        return ""
    return dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def main():
    url = "https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd"

    cookie = ""
    user_agent = ""

    headers = {
        "User-Agent": user_agent,
        "Cookie": cookie,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bilibili.com/",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        raise SystemExit(f"请求或解析失败：{e}")

    items = (payload.get("data") or {}).get("item") or []
    output = []

    for it in items:
        rcmd_reason_obj = it.get("rcmd_reason")
        rcmd_content = ""
        if isinstance(rcmd_reason_obj, dict):
            rcmd_content = rcmd_reason_obj.get("content") or ""

        entry = {
            "bvid": it.get("bvid", ""),
            "title": (it.get("title") or "").strip(),
            "duration": format_duration(it.get("duration")),
            "owner": (it.get("owner") or {}).get("name", ""),
            "pubdate": format_pubdate(it.get("pubdate")),
            "view": (it.get("stat") or {}).get("view", 0),
            "like": (it.get("stat") or {}).get("like", 0),
            "rcmd_reason": rcmd_content,
            "uri": it.get("uri", ""),
        }
        output.append(entry)

    with open("bilibili.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"已保存 {len(output)} 条记录到 bilibili.json")


if __name__ == "__main__":
    main()