import dolphindb as ddb
import pandas as pd
import matplotlib.pyplot as plt
import alphalens.plotting as plotting
import warnings

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

query = """
select factor_value
from loadTable("dfs://crypto_kline_1h", "hourfactor") pivot by symbol, open_time, factor_name
"""
df = s.run(query)

plt.figure(figsize=(12, 5))
plt.plot(df['open_time'], df['momentum5h'])
plt.title("BTCUSDT 动量因子（5小时）")
plt.xlabel("时间")
plt.ylabel("Momentum")
plt.grid(True)
plt.tight_layout()
plt.show()



s.run("use alphalens")
## 因子分布分析
script_plot_quantile_statistics_table = '''
    plot_quantile_statistics_table(factor_data)
'''
ret = s.run(script_plot_quantile_statistics_table)
plotting.plot_quantile_statistics_table(ret)