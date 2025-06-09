import dolphindb as ddb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import seaborn as sns


# 中文字体设置
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# === 配置 DolphinDB 连接 ===
ddb_host = "192.168.100.43"
ddb_port = 7739
ddb_user = "admin"
ddb_pass = "123456"

s = ddb.session()
s.connect(ddb_host, ddb_port, ddb_user, ddb_pass)

# === 获取每笔交易数据 ===
df = s.run("select * from portfolio_combo where rebalance_time> 2023.01.01 order by rebalance_time ")

# === 按时间聚合收益 ===
df_group = df.groupby("rebalance_time")["return"].mean().reset_index()
df_group.rename(columns={"rebalance_time": "time", "return": "avg_return"}, inplace=True)
df_group["cum_return"] = (1 + df_group["avg_return"]).cumprod()

# === 计算统计指标 ===
def compute_metrics(df):
    ret = df["avg_return"]
    freq_per_year = 1460  # 每6小时调仓一次

    win_rate = (ret > 0).mean()
    total_return = df["cum_return"].iloc[-1] - 1
    ann_return = (1 + total_return) ** (freq_per_year / len(ret)) - 1
    ann_vol = ret.std() * (freq_per_year ** 0.5)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    max_drawdown = ((df["cum_return"].cummax() - df["cum_return"]) / df["cum_return"].cummax()).max()

    return {
        "胜率": f"{win_rate:.2%}",
        "总收益": f"{total_return:.2%}",
        "年化收益": f"{ann_return:.2%}",
        "年化波动率": f"{ann_vol:.2%}",
        "夏普比": f"{sharpe:.2f}",
        "最大回撤": f"{max_drawdown:.2%}",
    }


metrics = compute_metrics(df_group)

# === 合并累计收益回rebalance点上 ===
df["rebalance_time"] = pd.to_datetime(df["rebalance_time"])
df_group["time"] = pd.to_datetime(df_group["time"])

# === 收益曲线 ===
# 只画累计收益线 + 注释，不加 scatter 点
plt.figure(figsize=(14, 6))
plt.plot(df_group["time"], df_group["cum_return"], label="累计收益", color="blue")

text = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
plt.gcf().text(0.75, 0.5, text, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

plt.title("策略累计收益")
plt.xlabel("时间")
plt.ylabel("累计收益")
plt.grid(True)
plt.axhline(1, linestyle='--', color='gray')
plt.legend()
plt.tight_layout()
plt.show()


# === 收益曲线 ===
df['loss_flag'] = (df['return'] <= -0.03)
stop_loss_ratio = df['loss_flag'].mean()
print(f"止损触发比例：{stop_loss_ratio:.2%}")




# === 收益分布 ===
plt.figure(figsize=(8,4))
sns.histplot(df["return"], bins=40, kde=True, color="gray")
plt.axvline(0, linestyle="--", color="black")
plt.title("每笔交易收益分布")
plt.xlabel("单笔收益")
plt.ylabel("频数")
plt.grid(True)
plt.show()



# 读取优化结果
df = s.run("select * from opt_results")

# 按总收益排序，查看 top10 参数组合
top_params = df.sort_values(by="totalReturn", ascending=False).head(10)
print(top_params)

import seaborn as sns
import matplotlib.pyplot as plt

pivot = df.pivot_table(values="totalReturn", index="lookback", columns="holding")

plt.figure(figsize=(8,6))
sns.heatmap(pivot, annot=True, fmt=".2%", cmap="YlGnBu")
plt.title("不同回看窗口和持仓周期下的总收益")
plt.show()
