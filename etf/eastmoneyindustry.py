import requests
import json
import re
from datetime import datetime

def fetch_em_column_news(page_index=1, column_id="366", page_size=20):
    url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
    timestamp = int(datetime.now().timestamp() * 1000)
    params = {
        "client": "web",
        "biz": "web_news_col",
        "column": column_id,
        "order": "1",
        "needInteractData": "0",
        "page_index": page_index,
        "page_size": page_size,
        "fields": "code,showTime,title,mediaName,summary,image,url,uniqueUrl,Np_dst",
        "types": "1,20",
        "callback": f"jQuery{timestamp}",
        "req_trace": str(timestamp),
        "_": str(timestamp)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.eastmoney.com/",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    resp = requests.get(url, headers=headers, params=params)
    # print(resp.text[:300])  # 可选调试输出

    match = re.search(r'^[^(]+\((.*)\)$', resp.text.strip())
    if not match:
        print("❌ JSONP 数据解析失败")
        return []

    data = json.loads(match.group(1))
    news_list = data.get("data", {}).get("list", [])
    return [{
        "time": item.get("showTime"),
        "title": item.get("title"),
        "summary": item.get("summary"),
        "media": item.get("mediaName"),
        "url": item.get("url")
    } for item in news_list]

all_news = fetch_em_column_news(page_index=1, column_id="372")

for item in all_news:
    print(f"[{item['time']}] {item['title']}")
    print(f"摘要: {item['summary']}")
    print(f"来源: {item['media']} 🔗 {item['url']}")
    print("———")
