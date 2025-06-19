import requests
import json
import re
from datetime import datetime

def fetch_eastmoney_news(page=1):
    url = "https://np-waplist.eastmoney.com/comm/wap/getlist"
    params = {
        "interact": "1",
        "client": "wap_sf",
        "biz": "wap_stock",
        "fcolName": "columns",
        "fcolValue": "407",
        "type": "1,20",
        "order": "2",
        "pageIndex": page,
        "pageSize": "30",
        "callback": f"jQuery{datetime.now().timestamp()}",
        "_": str(int(datetime.now().timestamp() * 1000))
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    resp = requests.get(url, headers=headers, params=params)
    match = re.search(r'jQuery.*?\((.*)\)', resp.text)
    if not match:
        print("❌ 无法提取 JSON")
        return []

    data = json.loads(match.group(1))
    news_list = data['data']['list']
    return [{
        "time": item.get("Art_ShowTime"),
        "title": item.get("Art_Title"),
        "url": item.get("Art_Url")
    } for item in news_list]


# # 示例：抓第一页
# news_today = fetch_eastmoney_news(page=1)

# # 打印部分结果
# for n in news_today:
#     print(f"[{n['time']}] {n['title']}")
#     print(f"🔗 {n['url']}\n")



def fetch_eastmoney_news_all(max_pages=10, stop_date=None):
    all_news = []
    for page in range(1, max_pages + 1):
        news = fetch_eastmoney_news(page)
        if not news:
            break

        all_news.extend(news)

        # 如果指定了停止时间，例如只要今天的新闻
        if stop_date:
            if any(datetime.strptime(n['time'], "%Y-%m-%d %H:%M:%S").date() < stop_date for n in news):
                break
    return all_news

# 使用示例：抓取最多5页，直到新闻不是今天为止
today = datetime.now().date()
all_today_news = fetch_eastmoney_news_all(max_pages=5, stop_date=today)

for n in all_today_news:
    print(f"[{n['time']}] {n['title']}")
    print(f"🔗 {n['url']}\n")
