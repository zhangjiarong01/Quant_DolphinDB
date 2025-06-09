import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import dolphindb as ddb

# === 连接 DolphinDB ===
# DolphinDB连接参数
ddb_host = "192.168.100.43"      # 替换为你的地址
ddb_port = 7739
ddb_user = "admin"
ddb_pass = "123456"

# 建立DolphinDB连接
s = ddb.session()
s.connect(ddb_host, ddb_port, ddb_user, ddb_pass)


# === 支持的因子列表 ===
factor_list = [
    "amplitude", "reverse_6", "turnover_6", "volatility_6", "vwap_gap", "combo_reverse_amp"
]

st.title("📈 因子分组净值曲线面板（交互可视化）")
selected_factor = st.selectbox("请选择因子：", factor_list)

# === 加载数据 ===
table_name = f"ic_ts_{selected_factor}"
df = s.run(table_name)
df['date'] = pd.to_datetime(df['date'])
df = df.set_index("date")

# === 颜色设置：色盲友好 ===
color_palette = [
    "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#a65628", "#f781bf", "#999999"
]

# === 生成 Plotly 图表 ===
fig = go.Figure()
for i, col in enumerate(df.columns):
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[col],
        mode='lines',
        name=col,
        line=dict(color=color_palette[i % len(color_palette)], width=2),
        hovertemplate="时间：%{x}<br>净值：%{y:.4f}<extra></extra>"
    ))

fig.update_layout(
    title=f"因子 `{selected_factor}` 的分组净值曲线",
    xaxis_title="时间",
    yaxis_title="净值",
    hovermode="x unified",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)
