import tushare as ts
import pandas as pd

# === 设置 Token ===
ts.set_token("adcf5802584d3f341ad1daadc82e3cc181cdfe52b2055493a5342e3f")  # 替换为你的 token
pro = ts.pro_api()

# === 拉取 LPR（1年期）===
lpr = pro.shibor_lpr(start_date='20150101', end_date='20250614', fields='date,1y')
lpr['date'] = pd.to_datetime(lpr['date'])
lpr['month'] = lpr['date'].dt.strftime('%Y%m')
lpr['1y'] = pd.to_numeric(lpr['1y'], errors='coerce')
lpr = lpr.sort_values('month').drop_duplicates('month')

# === 拉取 CPI ===
cpi = pro.cn_cpi(start_m='201501', end_m='202507', fields='month,nt_yoy')
cpi = cpi.rename(columns={'nt_yoy': 'cpi_yoy'})

# === 拉取 PPI ===
ppi = pro.cn_ppi(start_m='201501', end_m='202507', fields='month,ppi_yoy')

# === 拉取 PMI（制造业）===
pmi = pro.cn_pmi(start_m='201501', end_m='202507', fields='month,pmi010000')
pmi = pmi.rename(columns={'pmi010000': 'pmi'})

# === 拉取社融（月增量）===
sf = pro.sf_month(start_m='201501', end_m='202507', fields='month,inc_month')
sf['inc_month'] = pd.to_numeric(sf['inc_month'], errors='coerce')

# === 合并为统一宏观数据表 ===
df = lpr[['month', '1y']].rename(columns={'1y': 'lpr_1y'}).copy()
df = df.merge(cpi, on='month', how='left')
df = df.merge(ppi, on='month', how='left')
df = df.merge(pmi, on='month', how='left')
df = df.merge(sf, on='month', how='left')

# === 类型转换与排序 ===
df['month'] = df['month'].astype(int)
df = df.sort_values('month').reset_index(drop=True)

# === 输出检查 ===
print("\n✅ 宏观原始变量（连续数值）表：")
print(df.tail(6))

# === 可选：保存为 CSV ===
df.to_csv("macro_scores.csv", index=False)
