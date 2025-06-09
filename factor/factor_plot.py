import dolphindb as ddb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import seaborn as sns

# 设置中文字体为 SimHei（黑体），避免中文乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# DolphinDB连接参数
ddb_host = "192.168.100.43"      # 替换为你的地址
ddb_port = 7739
ddb_user = "admin"
ddb_pass = "123456"

# 建立DolphinDB连接
s = ddb.session()
s.connect(ddb_host, ddb_port, ddb_user, ddb_pass)


s.run("1;")


# 假设你已经从 DolphinDB 拉取成 DataFrame 命名为 df
df = s.run("ic_ts_momentum_6")  # 伪代码


df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# 画图
plt.figure(figsize=(12, 6))
for col in df.columns:
    plt.plot(df.index, df[col], label=col)

plt.title("IC Quantile Net Value Curve: momentum_6")
plt.xlabel("Date")
plt.ylabel("Net Value")
plt.legend(title="Quantile")
plt.grid(True)
plt.tight_layout()
plt.show()



import dolphindb as ddb
import pandas as pd
import matplotlib.pyplot as plt

# === 连接 DolphinDB
s = ddb.session()
s.connect("localhost", 8848, "admin", "123456")

# === 你要可视化的表名列表
factor_names = [
    "amplitude", "momentum20h", "momentum5h", "momentum_6",
    "reverse_6", "turnover_6", "volatility_6", "vwap_gap"
]

# === 遍历并画图
for factor in factor_names:
    table_name = f"ic_ts_{factor}"
    try:
        df = s.run(table_name)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index("date")
        
        # 画每个 quantile 的净值曲线
        plt.figure(figsize=(12, 5))
        for col in df.columns:
            if col != "date" and df[col].dtype.kind in "f":
                plt.plot(df.index, df[col], label=col)

        plt.title(f"因子分层净值曲线：{factor}")
        plt.xlabel("时间")
        plt.ylabel("净值")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"⚠️ 表 {table_name} 读取失败：{e}")
