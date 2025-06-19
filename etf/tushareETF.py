import tushare as ts
import pandas as pd
import time

# 初始化 tushare
ts.set_token('adcf5802584d3f341ad1daadc82e3cc181cdfe52b2055493a5342e3f')  # 替换成你的 Tushare token
pro = ts.pro_api()

# 设置多个 ETF 代码
etf_codes = ['510300.SH', '510500.SH', '159915.SZ']  # 可根据需求扩展
start_date = '20150101'
end_date = '20250614'

# 获取单个ETF每日行情
def get_etf_daily(ts_code, start_date, end_date):
    all_data = []
    offset = 0
    while True:
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date, limit=2000, offset=offset)
        if df.empty:
            break
        all_data.append(df)
        offset += 2000
        time.sleep(0.3)  # 防止频率限制
    if all_data:
        result = pd.concat(all_data).sort_values(by='trade_date')
        result['ts_code'] = ts_code  # 加上代码列以便识别
        return result
    else:
        return pd.DataFrame()

# 合并所有ETF数据
all_etf_data = []

for code in etf_codes:
    print(f"正在下载：{code}")
    df = get_etf_daily(code, start_date, end_date)
    if not df.empty:
        all_etf_data.append(df)

# 合并为总表
final_df = pd.concat(all_etf_data).sort_values(['ts_code', 'trade_date'])

# 输出样例与保存
print("ETF总数据样例：")
print(final_df.head())

final_df.to_csv("etf_prices.csv", index=False, encoding='utf-8-sig')
print("✅ etf_prices.csv")
