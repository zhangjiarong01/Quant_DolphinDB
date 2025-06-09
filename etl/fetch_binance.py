import os
import json
import pandas as pd
import requests
import zipfile
import io
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import dolphindb as ddb

# === 配置 ===
ddb_host = "192.168.100.43"
ddb_port = 7739
ddb_user = "admin"
ddb_pass = "123456"
db_path = "dfs://crypto_kline_1h"
table_name = "kline_1h"
tmp_dir = "tmp"
parquet_dir = "parquet_cache"
log_file = "import_log.json"

# 初始化 DolphinDB 连接
s = ddb.session()
s.connect(ddb_host, ddb_port, ddb_user, ddb_pass)
appender = ddb.TableAppender(db_path, table_name, s)

# 本地目录准备
os.makedirs(tmp_dir, exist_ok=True)
os.makedirs(parquet_dir, exist_ok=True)

# 导入日志机制
try:
    with open(log_file, "r") as f:
        import_log = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    import_log = {}

def already_imported(symbol, year, month):
    return f"{symbol}-{year}-{month:02}" in import_log

def mark_imported(symbol, year, month):
    import_log[f"{symbol}-{year}-{month:02}"] = True
    with open(log_file, "w") as f:
        json.dump(import_log, f, indent=2)

# 下载并解压
def download_and_extract(symbol, interval, year, month):
    url = f"https://data.binance.vision/data/spot/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{year}-{month:02}.zip"
    try:
        print(f"📥 下载：{url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()  # 如果状态码不是200，会抛出HTTPError异常
        
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(tmp_dir)
            filename = z.namelist()[0]
            return os.path.join(tmp_dir, filename)
    except Exception as e:
        with open("fail_log.txt", "a") as f:
            f.write(f"{datetime.now().isoformat()} | {symbol}-{year}-{month:02} | ERROR: {str(e)}\n")
        print(f"⚠️ 下载失败：{url} - {e}")
        return None

# 转换为 Parquet
def load_csv_to_parquet(csv_path, symbol):
    try:
        df = pd.read_csv(csv_path, header=None)
        df.columns = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "n_trades",
            "taker_base", "taker_quote", "ignore"
        ]
        df["symbol"] = symbol
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')
        df["update_time"] = datetime.now()
        df.drop(columns=["ignore"], inplace=True)
        
        # 确保目录存在
        os.makedirs(parquet_dir, exist_ok=True)
        
        # 使用更安全的文件名
        first_date = df['open_time'].iloc[0].strftime('%Y%m') if not df.empty else 'nodata'
        parquet_path = os.path.join(parquet_dir, f"{symbol}_{first_date}.parquet")
        df.to_parquet(parquet_path, index=False)
        return parquet_path
    except Exception as e:
        print(f"❌ 转换失败：{csv_path} - {e}")
        return None

# 主处理函数
def process(symbol, interval, year, month):
    if already_imported(symbol, year, month):
        print(f"⏩ 跳过 {symbol}-{year}-{month:02}（日志已记录）")
        return
    
    csv_path = download_and_extract(symbol, interval, year, month)
    if not csv_path:
        return
    
    parquet_path = load_csv_to_parquet(csv_path, symbol)
    if not parquet_path:
        return
    
    try:
        df = pd.read_parquet(parquet_path)
        appender.append(df)
        print(f"✅ 写入成功：{symbol}-{year}-{month:02}")
        mark_imported(symbol, year, month)
    except Exception as e:
        print(f"❌ 写入DolphinDB失败：{symbol}-{year}-{month:02} - {e}")
    finally:
        # 清理临时文件
        if csv_path and os.path.exists(csv_path):
            try:
                os.remove(csv_path)
            except Exception as e:
                print(f"⚠️ 删除临时文件失败：{csv_path} - {e}")
        
        if parquet_path and os.path.exists(parquet_path):
            try:
                os.remove(parquet_path)
            except Exception as e:
                print(f"⚠️ 删除临时文件失败：{parquet_path} - {e}")

# 并行处理入口
def run_batch(symbols, years, months, max_workers=5):
    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for symbol in symbols:
            for year in years:
                for month in months:
                    tasks.append(executor.submit(process, symbol, "1h", year, month))
        
        # 等待所有任务完成
        for task in tasks:
            try:
                task.result()
            except Exception as e:
                print(f"⚠️ 任务执行失败: {e}")

# ======= 多币种批量导入入口 =======
if __name__ == "__main__":
    symbols = [ "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT",
    "TRXUSDT", "SHIBUSDT", "LINKUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "BCHUSDT", "ETCUSDT", "XLMUSDT", "FILUSDT",
    "HBARUSDT", "ICPUSDT", "APTUSDT", "ARBUSDT", "NEARUSDT", "OPUSDT", "VETUSDT", "GRTUSDT", "MKRUSDT", "SANDUSDT",
    "EOSUSDT", "AAVEUSDT", "RUNEUSDT", "THETAUSDT", "QNTUSDT", "FTMUSDT", "XTZUSDT", "FLOWUSDT", "CHZUSDT", "EGLDUSDT",
    "AXSUSDT", "SNXUSDT", "KAVAUSDT", "TWTUSDT", "IMXUSDT", "CRVUSDT", "GMXUSDT", "CFXUSDT", "DYDXUSDT", "LDOUSDT",
    "ZECUSDT", "1INCHUSDT", "ALGOUSDT", "ROSEUSDT", "COMPUSDT", "YFIUSDT", "STXUSDT", "WOOUSDT", "ENSUSDT", "IOTAUSDT",
    "KSMUSDT", "CELOUSDT", "GMTUSDT", "OCEANUSDT", "BALUSDT", "ZILUSDT", "ANKRUSDT", "LINAUSDT", "SKLUSDT", "XEMUSDT",
    "BLZUSDT", "SXPUSDT", "ARPAUSDT", "BANDUSDT", "COTIUSDT", "RLCUSDT", "DGBUSDT", "STMXUSDT", "MTLUSDT", "NKNUSDT",
    "BELUSDT", "HOOKUSDT", "HIGHUSDT", "JOEUSDT", "TUSDT", "TRUUSDT", "PEOPLEUSDT", "MDTUSDT", "FETUSDT", "CKBUSDT",
    "DODOUSDT", "BNTUSDT", "OMGUSDT", "VTHOUSDT", "WNXMUSDT", "POWRUSDT", "REIUSDT", "FLMUSDT", "XNOUSDT", "RSRUSDT"]
  # 修正了这里的重复赋值
    run_batch(symbols=symbols, years=range(2021, 2024), months=range(1, 13), max_workers=8)
    