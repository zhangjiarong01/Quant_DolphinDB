import tushare as ts
import pandas as pd

ts.set_token('2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211')
pro = ts.pro_api()

# 中证500每年6月和12月调整，我们取过去几次调仓日期
adjustment_dates = [
    ('202212', '20221201', '20221231'),  # 2022年12月调整
    ('202306', '20230601', '20230630'),  # 2023年6月调整
    ('202312', '20231201', '20231231'),  # 2023年12月调整
    ('202406', '20240601', '20240630'),   # 2024年6月调整(最近一次)
    ('202412', '20241201', '20241231'),
    ('202406', '20240601', '20240630')
]

weights_data = {}
for month, start, end in adjustment_dates:
    try:
        df = pro.index_weight(index_code='000510.SH', start_date=start, end_date=end)
        if not df.empty:
            weights_data[month] = df
            print(f"成功获取 {month} 数据，记录数: {len(df)}")
        else:
            print(f"警告: {month} 无数据")
    except Exception as e:
        print(f"获取 {month} 数据时出错: {e}")

# 分析调仓变化
changes = []
months = list(weights_data.keys())
for i in range(1, len(months)):
    prev_month = months[i-1]
    curr_month = months[i]
    
    prev_df = weights_data[prev_month]
    curr_df = weights_data[curr_month]
    
    prev_stocks = set(prev_df['con_code'])
    curr_stocks = set(curr_df['con_code'])
    
    added = curr_stocks - prev_stocks
    removed = prev_stocks - curr_stocks
    
    for stock in added:
        changes.append({
            "adjustment_date": curr_month,
            "change_type": "add",
            "con_code": stock,
            "con_name": curr_df.loc[curr_df['con_code'] == stock, 'con_name'].values[0] if 'con_name' in curr_df.columns else ""
        })
    
    for stock in removed:
        changes.append({
            "adjustment_date": curr_month,
            "change_type": "remove", 
            "con_code": stock,
            "con_name": prev_df.loc[prev_df['con_code'] == stock, 'con_name'].values[0] if 'con_name' in prev_df.columns else ""
        })

# 保存结果
if changes:
    changes_df = pd.DataFrame(changes)
    changes_df.to_csv("csia500.csv", index=False, encoding='utf_8_sig')
    print("\n调仓变化统计:")
    print(changes_df)
    print("\n✅ 保存完成: csia500.csv")
else:
    print("未获取到有效的调仓变化数据")


df = pro.stk_mins(ts_code='000591.SZ', freq='5min', start_date='2023-08-25 09:00:00', end_date='2023-08-25 19:00:00')



import akshare as ak

# 示例：获取贵州茅台(600519) 2023-12-13的1分钟K线
df = ak.stock_zh_a_hist_min_em(
    symbol="600519",       # 股票代码（不带.SH/.SZ）
    period="1",           # 1分钟线
    start_date="2023-12-13 09:30:00",
    end_date="2023-12-13 15:00:00",
    adjust=""             # 不复权
)
print(df.head())


import akshare as ak

# 获取 2025-06-16 的 1分钟K线数据（以五粮液为例）
df = ak.stock_zh_a_minute(symbol="000858", period="1", adjust="", start_date="20250616", end_date="20250616")

print(df.head())
