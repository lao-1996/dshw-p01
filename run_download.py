"""
01_download 替代脚本 —— 绕过 notebook JSON 格式问题
直接用脚本下载所有数据，输出到 data/ 目录
"""
import akshare as ak
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime

print(f"akshare 版本: {ak.__version__}")
print(f"数据下载开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("数据源: 新浪 + 央行 + akshare")

# ============================================================
# 股票列表
# ============================================================
stocks = [
    {"code": "000001", "name": "平安银行", "industry": "银行"},
    {"code": "600036", "name": "招商银行", "industry": "银行"},
    {"code": "002594", "name": "比亚迪",   "industry": "汽车"},
    {"code": "300750", "name": "宁德时代", "industry": "能源"},
    {"code": "601012", "name": "隆基绿能", "industry": "能源"},
    {"code": "600519", "name": "贵州茅台", "industry": "白酒"},
    {"code": "000063", "name": "中兴通讯", "industry": "通讯"},
    {"code": "002352", "name": "顺丰控股", "industry": "物流"},
    {"code": "600048", "name": "保利发展", "industry": "房地产"},
    {"code": "002475", "name": "立讯精密", "industry": "通讯"},
]

# ============================================================
# 1. 下载个股日度行情 (新浪 source: stock_zh_a_daily)
# ============================================================
end_date = datetime.now().strftime("%Y%m%d")
os.makedirs("data/stock", exist_ok=True)

print("\n=== 1. 下载个股日度行情 ===")
for stock in stocks:
    code_ = stock["code"]
    name_ = stock["name"]
    prefix = "sh" if code_.startswith("6") else "sz"
    symbol = f"{prefix}{code_}"
    try:
        df = ak.stock_zh_a_daily(symbol=symbol, adjust="hfq")
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= "2020-01-01") & (df["date"] <= end_date)]
        cols = ["date", "open", "high", "low", "close", "volume", "amount"]
        df = df[cols].rename(columns={"amount": "turnover"})
        path = f"data/stock/stock_{code_}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"  OK  stock_{code_} ({name_})  shape={df.shape}")
    except Exception as e:
        print(f"  FAIL  stock_{code_} ({name_})  {e}")
    time.sleep(0.5)

# ============================================================
# 2. 下载指数数据
# ============================================================
print("\n=== 2. 下载市场指数 ===")
os.makedirs("data/index", exist_ok=True)

# 沪深300
try:
    hs300 = ak.stock_zh_index_daily(symbol="sh000300")
    hs300["date"] = pd.to_datetime(hs300["date"])
    hs300 = hs300[(hs300["date"] >= "2020-01-01") & (hs300["date"] <= end_date)]
    hs300.to_csv("data/index/index_000300.csv", index=False, encoding="utf-8-sig")
    print(f"  OK  index_000300 (沪深300)  shape={hs300.shape}")
except Exception as e:
    print(f"  FAIL  index_000300  {e}")

# 中证500
try:
    zz500 = ak.stock_zh_index_daily(symbol="sh000905")
    zz500["date"] = pd.to_datetime(zz500["date"])
    zz500 = zz500[(zz500["date"] >= "2020-01-01") & (zz500["date"] <= end_date)]
    zz500.to_csv("data/index/index_000905.csv", index=False, encoding="utf-8-sig")
    print(f"  OK  index_000905 (中证500)  shape={zz500.shape}")
except Exception as e:
    print(f"  FAIL  index_000905  {e}")

# ============================================================
# 3. 宏观经济指标
# ============================================================
print("\n=== 3. 宏观经济指标 ===")
os.makedirs("data/macro", exist_ok=True)

# CPI
try:
    cpi = ak.macro_china_cpi_monthly()
    cpi.to_csv("data/macro/macro_cpi.csv", index=False, encoding="utf-8-sig")
    print(f"  OK  macro_cpi  shape={cpi.shape}")
except Exception as e:
    print(f"  FAIL  macro_cpi  {e}")

# M2 (使用 macro_china_money_supply)
try:
    m2_raw = ak.macro_china_money_supply()
    m2_df = m2_raw[["月份", "货币和准货币(M2)-同比增长"]].copy()
    m2_df = m2_df.rename(columns={
        "月份": "month",
        "货币和准货币(M2)-同比增长": "m2_yoy"
    })
    m2_df = m2_df.dropna(subset=["m2_yoy"])
    m2_df.to_csv("data/macro/macro_m2.csv", index=False, encoding="utf-8-sig")
    print(f"  OK  macro_m2  shape={m2_df.shape}")
except Exception as e:
    print(f"  FAIL  macro_m2  {e}")

# ============================================================
# 4. 财务指标 (ROE + 销售净利率)
# ============================================================
print("\n=== 4. 财务指标 ===")
os.makedirs("data/finance", exist_ok=True)

finance_long_list = []

for stock in stocks:
    code_ = stock["code"]
    name_ = stock["name"]
    try:
        df = ak.stock_financial_abstract(symbol=code_)

        # Find ROE and 销售净利率 rows
        roe_rows = df[df["指标"] == "净资产收益率(ROE)"]
        npm_rows = df[df["指标"] == "销售净利率"]

        if roe_rows.empty and npm_rows.empty:
            print(f"  WARN  {name_} 未找到 ROE/净利率指标")
            continue

        # Date columns (e.g., 20201231, 20211231...)
        date_cols = [c for c in df.columns
                     if c not in ["选项", "指标"]
                     and str(c).isdigit()
                     and len(str(c)) == 8]

        for col in date_cols:
            year = int(str(col)[:4])
            if year < 2020:
                continue

            if not roe_rows.empty:
                val = pd.to_numeric(roe_rows.iloc[0][col], errors="coerce")
                if not pd.isna(val):
                    finance_long_list.append({
                        "code": code_, "name": name_, "year": year,
                        "indicator": "ROE", "value": float(val)
                    })

            if not npm_rows.empty:
                val = pd.to_numeric(npm_rows.iloc[0][col], errors="coerce")
                if not pd.isna(val):
                    finance_long_list.append({
                        "code": code_, "name": name_, "year": year,
                        "indicator": "net_profit_margin", "value": float(val)
                    })

        print(f"  OK  finance_{code_} ({name_})")

    except Exception as e:
        print(f"  FAIL  finance_{code_} ({name_})  {e}")

    time.sleep(0.5)

finance_long_df = pd.DataFrame(finance_long_list)
finance_long_df.to_csv("data/finance/finance_ratios.csv", index=False, encoding="utf-8-sig")
print(f"\n  财务长格式: shape={finance_long_df.shape}")

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print(f"数据下载完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 检查文件
print("\n生成的文件:")
for root, dirs, files in os.walk("data"):
    for f in sorted(files):
        fp = os.path.join(root, f)
        size = os.path.getsize(fp)
        print(f"  {fp} ({size:,} bytes)")
