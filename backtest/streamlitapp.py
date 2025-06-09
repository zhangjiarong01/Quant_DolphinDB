import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dolphindb as ddb

# === 连接 DolphinDB ===
@st.cache_resource
def connect_ddb():
    s = ddb.session()
    s.connect("192.168.100.43", 7739, "admin", "123456")
    return s

s = connect_ddb()

st.title("🧪 策略回测可视化")

# === 参数选择 ===
st.sidebar.header("参数设置")
portfolio_table = st.sidebar.text_input("回测结果表名", "portfolio1")
show_trades = st.sidebar.checkbox("显示盈亏点标记", value=True)

# === 拉取数据 ===
try:
    df = s.run(f"select * from {portfolio_table} order by rebalance_time")
except:
    st.error("❌ 无法连接到 DolphinDB 或表不存在")
    st.stop()

# === 聚合并计算累计收益 ===
df_group = df.groupby("rebalance_time")["return"].mean().reset_index()
df_group.rename(columns={"rebalance_time": "time", "return": "avg_return"}, inplace=True)
df_group["cum_return"] = (1 + df_group["avg_return"]).cumprod()

# === 计算指标 ===
def compute_metrics(df):
    ret = df["avg_return"]
    win_rate = (ret > 0).mean()
    total_return = df["cum_return"].iloc[-1] - 1
    ann_return = (1 + total_return) ** (365 * 24 / len(ret)) - 1
    max_dd = ((df["cum_return"].cummax() - df["cum_return"]) / df["cum_return"].cummax()).max()
    return {
        "胜率": f"{win_rate:.2%}",
        "总收益": f"{total_return:.2%}",
        "年化收益": f"{ann_return:.2%}",
        "最大回撤": f"{max_dd:.2%}"
    }

metrics = compute_metrics(df_group)

# === 显示指标 ===
st.subheader("📊 策略表现指标")
st.dataframe(pd.DataFrame([metrics]))

# === 可视化图表 ===
st.subheader("📈 策略累计收益曲线")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_group["time"], df_group["cum_return"], label="累计收益", color="blue")

if show_trades:
    for idx, row in df.iterrows():
        color = "green" if row["return"] > 0 else "red"
        ax.scatter(row["rebalance_time"], np.nan, c=color, s=10, alpha=0.6)

ax.axhline(1, linestyle='--', color='gray')
ax.set_xlabel("时间")
ax.set_ylabel("累计收益")
ax.grid(True)
ax.legend()
st.pyplot(fig)
