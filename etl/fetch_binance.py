import os
import pandas as pd
import requests
import zipfile
import io
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import dolphindb as ddb

# 配置
ddb_host = "192.168.100.43"
ddb_port = 7739
ddb_user = "admin"
ddb_pass = "123456"
db_path = "dfs://crypto_kline_1h"
table_name = "kline_1h"
tmp_dir = "tmp"
parquet_dir = "parquet_cache"

# 初始化 DolphinDB 连接
s = ddb.session()
s.connect(ddb_host, ddb_port, ddb_user, ddb_pass)
appender = ddb.TableAppender(db_path, table_name, s)

# 创建本地缓存目录
os.makedirs(tmp_dir, exist_ok=True)
os.makedirs(parquet_dir, exist_ok=True)

# 下载并解压 Binance 数据
def download_and_extract(symbol, interval, year, month):
    url = f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02}.zip"
    try:
        print(f"📥 下载：{url}")
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            print(f"❌ 下载失败：{url}")
            return None

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(tmp_dir)
            filename = z.namelist()[0]
            return os.path.join(tmp_dir, filename)
    except Exception as e:
        print(f"⚠️ 下载/解压错误：{url} - {e}")
        return None

# 加载并转换为 Parquet
def load_csv_to_parquet(csv_path, symbol):
    try:
        df = pd.read_csv(csv_path, header=None)
        df.columns = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "n_trades",
            "taker_base", "taker_quote", "ignore"
        ]
        df["symbol"] = symbol
        df["symbol"] = df["symbol"].astype(str).astype("string")
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')
        df["update_time"] = datetime.now()
        df.drop(columns=["ignore"], inplace=True)

        if df.shape[1] != 13:
            raise ValueError("列数不匹配")

        parquet_path = os.path.join(parquet_dir, f"{symbol}_{df['open_time'].iloc[0].strftime('%Y%m')}.parquet")
        df.to_parquet(parquet_path, index=False)
        return parquet_path
    except Exception as e:
        print(f"❌ 转换失败：{csv_path} - {e}")
        return None

# 判断是否已有数据
def data_exists(symbol, start_time):
    try:
        query = f"""
        select count(*) from {table_name}
        where symbol = `{symbol} and open_time >= datetime("{start_time}")
        """
        count = s.run(query)
        return count > 0
    except:
        return False

# 主处理函数
def process(symbol, interval, year, month):
    csv_path = download_and_extract(symbol, interval, year, month)
    if not csv_path:
        return

    try:
        df_temp = pd.read_csv(csv_path, header=None)
        open_time = pd.to_datetime(df_temp[0][0], unit="ms")
        if data_exists(symbol, open_time.strftime("%Y-%m-%d %H:%M:%S")):
            print(f"⏩ 跳过 {symbol}-{year}-{month:02}（数据已存在）")
            os.remove(csv_path)
            return
    except:
        print(f"⚠️ 检查已存在数据失败：{csv_path}")
        return

    parquet_path = load_csv_to_parquet(csv_path, symbol)
    if parquet_path:
        df = pd.read_parquet(parquet_path)
        appender.append(df)
        print(f"✅ 写入成功：{symbol}-{year}-{month:02}")

    # 清理临时文件
    os.remove(csv_path)
    os.remove(parquet_path)

# 并行执行入口
def run_batch(symbols, years, months, max_workers=5):
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for symbol in symbols:
            for year in years:
                for month in months:
                    tasks.append(executor.submit(process, symbol, "1h", year, month))
        for task in tasks:
            task.result()

# 只执行函数，不自动跑

# ======= 多币种批量导入入口 =======
if __name__ == "__main__":
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"]
    years = range(2020, 2025)
    months = range(1, 13)
    run_batch(symbols, years, months, max_workers=6)

symbols = ["SOLUSDT", "ADAUSDT", "AVAXUSDT"]
years = range(2020, 2025)
months = range(1, 13)
run_batch(symbols, years, months, max_workers=6)