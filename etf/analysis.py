import pandas as pd
import statsmodels.api as sm

# === 1. 读取数据 === #
policy_df = pd.read_csv('policy_events.csv', parse_dates=['date'])
etf_df = pd.read_csv('etf_prices.csv', parse_dates=['trade_date']).rename(columns={'trade_date': 'date'})
flow_df = pd.read_csv('market_flows.csv', parse_dates=['date']).rename(columns={'1date': 'date'})
macro_df = pd.read_csv('macro_scores.csv')
macro_df['month'] = pd.to_datetime(macro_df['month'], format='%Y%m')

# === 2. 合并数据 === #
# 生成ETF每日涨跌（如果已有pct_chg字段可跳过）
etf_df = etf_df.sort_values('date')
etf_df['pct_chg'] = etf_df['close'].pct_change() * 100

# 合并政策冲击
merged = pd.merge(etf_df, policy_df, how='left', on='date')

# 合并资金流
merged = pd.merge(merged, flow_df[['date', 'super_large_netflow_pct', 'large_netflow_pct']], how='left', on='date')

# 合并宏观数据（月度对齐）
merged['month'] = merged['date'].dt.to_period('M').dt.to_timestamp()
merged = pd.merge(merged, macro_df[['month', 'macro_score']], how='left', on='month')

# 填充非冲击日为0
merged['shock'] = merged['shock'].fillna(0)
merged['liquidity'] = merged['liquidity'].fillna(0)
merged['fiscal'] = merged['fiscal'].fillna(0)
merged['structural'] = merged['structural'].fillna(0)

# === 3. 构建回归样本 === #
# 取有收益数据的行，作为分析期
reg_df = merged.dropna(subset=['pct_chg', 'macro_score'])

# === 4. 回归分析 === #
# 构建滞后一日收益
reg_df = reg_df.copy()
reg_df['ret_lead1'] = reg_df['pct_chg'].shift(-1)

# 构建回归变量
X = reg_df[['shock', 'super_large_netflow_pct', 'macro_score']]
X = sm.add_constant(X)
y = reg_df['ret_lead1']

# 确保 X 和 y 对齐并剔除缺失值
Xy = pd.concat([X, y], axis=1).dropna()
X = Xy.drop(columns='ret_lead1')
y = Xy['ret_lead1']

print("X shape:", X.shape)
print("y shape:", y.shape)
print("X columns:", X.columns)
print("样本日期范围：", reg_df['date'].min(), "~", reg_df['date'].max())
print("ret_lead1 非空样本数：", reg_df['ret_lead1'].notnull().sum())
print("shock 非0的日期：", reg_df[reg_df['shock'] == 1]['date'].tolist())

# 回归
model = sm.OLS(y, X).fit()
print(model.summary())

