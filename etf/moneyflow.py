import tushare as ts
import pandas as pd

# 初始化 Pro 接口
ts.set_token("2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211")  # 替换为你的 token
pro = ts.pro_api()

# 拉取数据（示例：2024年9月1日到9月30日）
df = pro.moneyflow_mkt_dc(start_date='20150101', end_date='20250630')

# 打印前几行检查数据
print(df.head())

# 保存为 CSV 文件
df.to_csv("moneyflow.csv", index=False, encoding='utf-8-sig')  # 加 encoding 防止中文乱码
