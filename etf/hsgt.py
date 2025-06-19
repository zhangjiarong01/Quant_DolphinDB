import tushare as ts
import pandas as pd
import time

# 设置 token
ts.set_token("2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211")
pro = ts.pro_api()

# 初始化空 DataFrame 用于汇总
all_data = pd.DataFrame()

# 逐年拉取数据
for year in range(2015, 2026):  # 从2015到2025
    start_date = f"{year}0101"
    end_date = f"{year}1231"

    try:
        df = pro.moneyflow_hsgt(start_date=start_date, end_date=end_date, limit=3000)
        print(f"✅ {year} 年数据获取成功：{len(df)} 条")
        all_data = pd.concat([all_data, df], ignore_index=True)
        time.sleep(1.5)  # 避免请求过快被限流
    except Exception as e:
        print(f"❌ {year} 年数据获取失败：{e}")

# 保存为 CSV
all_data.to_csv("hsgt_all_2015_2025.csv", index=False, encoding='utf-8-sig')
print("✅ 全部数据保存完成，文件名：hsgt_all_2015_2025.csv")
