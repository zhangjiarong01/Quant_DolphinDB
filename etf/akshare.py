import akshare as ak
import pandas as pd
from time import sleep

# 你那 21 个调入股票代码列表（东方财富格式，无需加 .SH/.SZ）
codes = ['000001', '600519', '000651']  # 用你实际的替换

all_data = []

for symbol in codes:
    try:
        df = ak.stock_zh_a_hist_min_em(
            symbol=symbol,
            period="1",
            start_date="2024-12-16 09:30:00",
            end_date="2024-12-16 15:00:00",
            adjust=""
        )
        df["symbol"] = symbol
        all_data.append(df)
        print(f"{symbol} ✅ {len(df)} rows")
        sleep(1.5)  # 避免请求过快被封
    except Exception as e:
        print(f"{symbol} ❌ {e}")

# 合并保存
final_df = pd.concat(all_data)
final_df.to_csv("minute_data_20241216.csv", index=False)
