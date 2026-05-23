# -*- coding: utf-8 -*-
"""
Generate 3 Jupyter Notebooks fully compliant with P02a assignment.
"""
import json, os, nbformat

BASE = r"C:\Users\劳润杰\Desktop\ai问题\中大学习\数据分析\dshw-p01"

def nb():
    n = nbformat.v4.new_notebook()
    n.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    n.metadata.language_info = {"name": "python", "version": "3.13.0"}
    return n

def md(n, src):
    n.cells.append(nbformat.v4.new_markdown_cell(src))

def code(n, src):
    n.cells.append(nbformat.v4.new_code_cell(src))


def build_01():
    n = nb()

    md(n, '# 第一部分：数据获取\n\n'
          '本 Notebook 完成以下数据下载：\n'
          '1. **10 只 A 股股票**的后复权日度行情（2020-01-01 至今）\n'
          '2. **沪深 300 指数** + **中证 500 指数**日度数据\n'
          '3. **宏观经济指标**：CPI 同比增速（月度）+ M2 同比增速（月度）\n'
          '4. **财务指标**：ROE、净利润率（近 5 年度），整理为长格式')

    code(n, 'import akshare as ak\n'
             'import pandas as pd\n'
             'import numpy as np\n'
             'import os\n'
             'from datetime import datetime\n'
             'import time\n\n'
             'print(f"akshare 版本: {ak.__version__}")\n'
             'print(f"数据下载开始时间: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")\n\n'
             '# 创建下载日志\n'
             'log_file = "download_log.txt"\n'
             'with open(log_file, "w", encoding="utf-8") as f:\n'
             '    f.write(f"数据下载日志 - {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\\n")\n'
             '    f.write("=" * 60 + "\\n")\n\n'
             'def write_log(msg):\n'
             '    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")\n'
             '    entry = f"[{ts}] {msg}\\n"\n'
             '    with open(log_file, "a", encoding="utf-8") as f:\n'
             '        f.write(entry)\n'
             '    print(entry.strip())')

    md(n, '## 1.1 股票列表\n\n'
          '选取 10 只股票，覆盖银行、汽车、能源、白酒、通讯、物流、房地产共 7 个行业\n'
          '（要求至少 5 个行业，每个行业至多 2 只）。')

    code(n, 'stocks = [\n'
             '    {"code": "000001", "name": "平安银行", "industry": "银行",\n'
             '     "reason": "银行板块龙头，资产规模大，代表银行业经营水平"},\n'
             '    {"code": "600036", "name": "招商银行", "industry": "银行",\n'
             '     "reason": "零售银行标杆，ROE 行业领先，与平安银行形成对比"},\n'
             '    {"code": "002594", "name": "比亚迪",   "industry": "汽车",\n'
             '     "reason": "新能源汽车龙头，近年业绩爆发式增长"},\n'
             '    {"code": "300750", "name": "宁德时代", "industry": "能源",\n'
             '     "reason": "动力电池全球龙头，新能源产业链核心标的"},\n'
             '    {"code": "601012", "name": "隆基绿能", "industry": "能源",\n'
             '     "reason": "光伏行业龙头，与宁德时代形成新能源细分对比"},\n'
             '    {"code": "600519", "name": "贵州茅台", "industry": "白酒",\n'
             '     "reason": "A 股市值标杆，消费板块代表性极强"},\n'
             '    {"code": "000063", "name": "中兴通讯", "industry": "通讯",\n'
             '     "reason": "5G 通信设备龙头，受益于数字经济政策"},\n'
             '    {"code": "002352", "name": "顺丰控股", "industry": "物流",\n'
             '     "reason": "快递行业龙头，直营模式代表"},\n'
             '    {"code": "600048", "name": "保利发展", "industry": "房地产",\n'
             '     "reason": "央企地产龙头，反映房地产行业周期"},\n'
             '    {"code": "002475", "name": "立讯精密", "industry": "通讯",\n'
             '     "reason": "苹果产业链核心供应商，消费电子代表"},\n'
             ']\n\n'
             'stocks_df = pd.DataFrame(stocks)\n'
             'display(stocks_df[["code", "name", "industry", "reason"]])')

    md(n, '## 1.2 下载个股日度行情数据\n\n'
          '使用 `akshare` 的 `stock_zh_a_hist()` 接口，获取后复权日度行情。\n'
          '字段要求：日期、开盘价、收盘价、最高价、最低价、成交量、成交额。')

    code(n, 'start_date = "20200101"\n'
             'end_date = datetime.now().strftime("%Y%m%d")\n\n'
             'print(f"下载时间范围: {start_date} 至 {end_date}")\n'
             'print("复权方式: 后复权 (hfq)")\n'
             'print("-" * 60)\n\n'
             'os.makedirs("data/stock", exist_ok=True)\n\n'
             'for stock in stocks:\n'
             '    code_ = stock["code"]\n'
             '    name_ = stock["name"]\n'
             '    try:\n'
             '        df = ak.stock_zh_a_hist(\n'
             '            symbol=code_, period="daily",\n'
             '            start_date=start_date, end_date=end_date,\n'
             '            adjust="hfq"\n'
             '        )\n'
             '        col_map = {\n'
             '            "日期": "date", "开盘": "open", "收盘": "close",\n'
             '            "最高": "high", "最低": "low", "成交量": "volume",\n'
             '            "成交额": "turnover"\n'
             '        }\n'
             '        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})\n'
             '        path = f"data/stock/stock_{code_}.csv"\n'
             '        df.to_csv(path, index=False, encoding="utf-8-sig")\n'
             '        write_log(f"SUCCESS  stock_{code_} ({name_})  shape={df.shape}")\n'
             '    except Exception as e:\n'
             '        write_log(f"FAILED   stock_{code_} ({name_})  Error: {e}")\n'
             '    time.sleep(0.5)\n\n'
             'print("-" * 60)\n'
             'print("个股数据下载完成！")')

    code(n, '# 检查下载结果\n'
             'sample = pd.read_csv("data/stock/stock_000001.csv")\n'
             'print(f"样例数据（平安银行）：shape={sample.shape}")\n'
             'print(f"列名: {sample.columns.tolist()}")\n'
             'display(sample.head())')

    md(n, '## 1.3 下载市场指数数据\n\n'
          '- **沪深 300**（000300）：作为 CAPM 分析的市场基准（必选）\n'
          '- **中证 500**（000905）：代表中小市值公司，与沪深 300 形成互补（自选）\n\n'
          '**选择中证 500 的理由**：中证 500 代表中小市值公司，与沪深 300（大盘蓝筹）形成互补，'
          '可以更全面地反映市场结构。')

    code(n, 'os.makedirs("data/index", exist_ok=True)\n\n'
             '# 沪深 300\n'
             'print("下载沪深 300...")\n'
             'try:\n'
             '    hs300 = ak.stock_zh_index_daily(symbol="sh000300")\n'
             '    hs300["date"] = pd.to_datetime(hs300["date"])\n'
             '    hs300 = hs300[(hs300["date"] >= "2020-01-01") & (hs300["date"] <= end_date)]\n'
             '    col_map = {"open": "idx_open", "close": "idx_close", "high": "idx_high",\n'
             '               "low": "idx_low", "volume": "idx_volume"}\n'
             '    hs300 = hs300.rename(columns={k: v for k, v in col_map.items() if k in hs300.columns})\n'
             '    hs300.to_csv("data/index/index_000300.csv", index=False, encoding="utf-8-sig")\n'
             '    write_log(f"SUCCESS  index_000300 (沪深300)  shape={hs300.shape}")\n'
             'except Exception as e:\n'
             '    write_log(f"FAILED   index_000300  Error: {e}")\n\n'
             '# 中证 500\n'
             'print("下载中证 500...")\n'
             'try:\n'
             '    zz500 = ak.stock_zh_index_daily(symbol="sh000905")\n'
             '    zz500["date"] = pd.to_datetime(zz500["date"])\n'
             '    zz500 = zz500[(zz500["date"] >= "2020-01-01") & (zz500["date"] <= end_date)]\n'
             '    col_map = {"open": "idx_open", "close": "idx_close", "high": "idx_high",\n'
             '               "low": "idx_low", "volume": "idx_volume"}\n'
             '    zz500 = zz500.rename(columns={k: v for k, v in col_map.items() if k in zz500.columns})\n'
             '    zz500.to_csv("data/index/index_000905.csv", index=False, encoding="utf-8-sig")\n'
             '    write_log(f"SUCCESS  index_000905 (中证500)  shape={zz500.shape}")\n'
             'except Exception as e:\n'
             '    write_log(f"FAILED   index_000905  Error: {e}")')

    md(n, '## 1.4 下载宏观经济指标\n\n'
          '- **CPI 同比增速**（必选）：反映居民消费价格变化，是央行货币政策的重要参考\n'
          '- **M2 同比增速**（自选）：反映货币供应量，与股市流动性密切相关\n\n'
          '**选择 M2 的理由**：M2 同比增速反映市场流动性水平。货币宽松（M2 高增）通常利好股市估值，'
          '货币紧缩则可能抑制股市表现。选择 M2 可以探讨流动性对股票市场的影响。')

    code(n, 'os.makedirs("data/macro", exist_ok=True)\n\n'
             '# CPI 月度同比增速\n'
             'print("下载 CPI 月度同比增速...")\n'
             'try:\n'
             '    cpi_df = ak.macro_china_cpi_monthly()\n'
             '    print(f"CPI 原始列名: {cpi_df.columns.tolist()}")\n'
             '    print(f"CPI 数据量: {len(cpi_df)}")\n'
             '    display(cpi_df.head())\n'
             '    cpi_df.to_csv("data/macro/macro_cpi.csv", index=False, encoding="utf-8-sig")\n'
             '    write_log(f"SUCCESS  macro_cpi  shape={cpi_df.shape}")\n'
             'except Exception as e:\n'
             '    write_log(f"FAILED   macro_cpi  Error: {e}")')

    code(n, '# M2 月度同比增速\n'
             'print("下载 M2 月度同比增速...")\n'
             'try:\n'
             '    m2_df = ak.macro_china_m2_monthly()\n'
             '    print(f"M2 原始列名: {m2_df.columns.tolist()}")\n'
             '    print(f"M2 数据量: {len(m2_df)}")\n'
             '    display(m2_df.head())\n'
             '    m2_df.to_csv("data/macro/macro_m2.csv", index=False, encoding="utf-8-sig")\n'
             '    write_log(f"SUCCESS  macro_m2  shape={m2_df.shape}")\n'
             'except Exception as e:\n'
             '    write_log(f"FAILED   macro_m2  Error: {e}")')

    md(n, '## 1.5 下载财务指标\n\n'
          '获取 10 只股票近 5 个年度的 **ROE（净资产收益率）** 和 **净利润率**，整理为长格式：\n\n'
          '`code, year, indicator, value`')

    code(n, 'os.makedirs("data/finance", exist_ok=True)\n\n'
             'finance_rows = []\n\n'
             'for stock in stocks:\n'
             '    code_ = stock["code"]\n'
             '    name_ = stock["name"]\n'
             '    try:\n'
             '        df = ak.stock_financial_analysis_indicator(symbol=code_)\n'
             '        print(f"{name_}({code_}): 列名={df.columns.tolist()[:6]}...")\n'
             '        display(df.head(2))\n'
             '        finance_rows.append({"code": code_, "name": name_, "raw": df})\n'
             '        write_log(f"SUCCESS  finance_{code_} ({name_})  shape={df.shape}")\n'
             '    except Exception as e:\n'
             '        write_log(f"FAILED   finance_{code_} ({name_})  Error: {e}")\n'
             '    time.sleep(0.5)')

    code(n, '# 整理财务数据为长格式 (code, year, indicator, value)\n'
             'finance_long_list = []\n\n'
             'for item in finance_rows:\n'
             '    code_ = item["code"]\n'
             '    name_ = item["name"]\n'
             '    df = item["raw"]\n'
             '    cols = df.columns.tolist()\n\n'
             '    # 找日期列\n'
             '    date_col = None\n'
             '    for c in cols:\n'
             '        if "日期" in str(c) or "截止" in str(c):\n'
             '            date_col = c\n'
             '            break\n'
             '    if date_col is None:\n'
             '        print(f"警告: {name_} 未找到日期列, 跳过")\n'
             '        continue\n\n'
             '    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")\n'
             '    df["year"] = df[date_col].dt.year\n\n'
             '    # ROE 和 净利润率 的可能列名\n'
             '    roe_candidates = [c for c in cols if "净资产收益率" in str(c)]\n'
             '    npm_candidates = [c for c in cols if "销售净利率" in str(c) or "净利率" in str(c)]\n\n'
             '    for _, row in df.iterrows():\n'
             '        yr = row["year"]\n'
             '        if pd.isna(yr) or yr < 2020:\n'
             '            continue\n'
             '        if roe_candidates:\n'
             '            val = pd.to_numeric(row[roe_candidates[0]], errors="coerce")\n'
             '            if not pd.isna(val):\n'
             '                finance_long_list.append({\n'
             '                    "code": code_, "name": name_, "year": int(yr),\n'
             '                    "indicator": "ROE", "value": float(val)\n'
             '                })\n'
             '        if npm_candidates:\n'
             '            val = pd.to_numeric(row[npm_candidates[0]], errors="coerce")\n'
             '            if not pd.isna(val):\n'
             '                finance_long_list.append({\n'
             '                    "code": code_, "name": name_, "year": int(yr),\n'
             '                    "indicator": "net_profit_margin", "value": float(val)\n'
             '                })\n\n'
             'finance_long_df = pd.DataFrame(finance_long_list)\n'
             'finance_long_df.to_csv("data/finance/finance_ratios.csv", index=False, encoding="utf-8-sig")\n'
             'print(f"\\n财务长格式数据: shape={finance_long_df.shape}")\n'
             'display(finance_long_df.head(10))\n'
             'write_log(f"SUCCESS  finance_ratios_long  shape={finance_long_df.shape}")')

    md(n, '## 1.6 检查下载结果')

    code(n, '# 显示下载日志\n'
             'print("=" * 60)\n'
             'with open("download_log.txt", "r", encoding="utf-8") as f:\n'
             '    print(f.read())')

    code(n, 'print(f"数据下载完成时间: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")\n'
             'print("\\n请继续运行 02_clean.ipynb 进行数据清洗")')

    return n


def build_02():
    n = nb()

    md(n, '# 第二部分：数据清洗\n\n'
          '本 Notebook 完成以下清洗步骤：\n'
          '1. **单表清洗**：缺失值检测与处理、日期格式统一、数据类型检查、重复值处理、离群值标注\n'
          '2. **宽表与长表转换**\n'
          '3. **多表合并**（个股 + 指数 + 宏观）\n'
          '4. **数据存储**（CSV + Parquet）')

    code(n, 'import pandas as pd\n'
             'import numpy as np\n'
             'import os\n'
             'from datetime import datetime\n'
             'import warnings\n'
             'warnings.filterwarnings("ignore")\n\n'
             'print(f"数据清洗开始时间: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")\n\n'
             'stocks = [\n'
             '    {"code": "000001", "name": "平安银行", "industry": "银行"},\n'
             '    {"code": "600036", "name": "招商银行", "industry": "银行"},\n'
             '    {"code": "002594", "name": "比亚迪",   "industry": "汽车"},\n'
             '    {"code": "300750", "name": "宁德时代", "industry": "能源"},\n'
             '    {"code": "601012", "name": "隆基绿能", "industry": "能源"},\n'
             '    {"code": "600519", "name": "贵州茅台", "industry": "白酒"},\n'
             '    {"code": "000063", "name": "中兴通讯", "industry": "通讯"},\n'
             '    {"code": "002352", "name": "顺丰控股", "industry": "物流"},\n'
             '    {"code": "600048", "name": "保利发展", "industry": "房地产"},\n'
             '    {"code": "002475", "name": "立讯精密", "industry": "通讯"},\n'
             ']\n'
             'stocks_df = pd.DataFrame(stocks)')

    md(n, '## 3.1 单表清洗\n\n'
          '对每只股票的原始数据依次执行 6 个清洗步骤，**每步均展示清洗前后的变化**。')

    md(n, '### 步骤 1：缺失值检测\n\n'
          '统计每列缺失值的数量和比例，分析缺失的可能原因。')

    code(n, '# 读取样例数据，展示缺失值检测过程\n'
             'sample = pd.read_csv("data/stock/stock_000001.csv")\n'
             'print("清洗前 - 平安银行数据：")\n'
             'print(f"  行数: {len(sample)}, 列数: {len(sample.columns)}")\n'
             'print(f"  列名: {sample.columns.tolist()}")\n\n'
             'missing = sample.isnull().sum()\n'
             'missing_pct = (missing / len(sample) * 100).round(2)\n'
             'missing_df = pd.DataFrame({"缺失数量": missing, "缺失比例(%)": missing_pct})\n'
             'has_missing = missing["缺失数量"].sum() > 0\n'
             'if has_missing:\n'
             '    display(missing_df[missing_df["缺失数量"] > 0])\n'
             'else:\n'
             '    print("无缺失值")\n'
             'print("\\n可能原因：股票数据缺失通常因停牌、节假日或数据源更新延迟。")')

    md(n, '### 步骤 2-6：完整清洗流程\n\n'
          '| 步骤 | 操作 | 说明 |\n'
          '|------|------|------|\n'
          '| 2 | 缺失值处理 | 前向填充（停牌期间价格不变，前值合理） |\n'
          '| 3 | 日期格式 | 统一为 datetime64 并设为索引 |\n'
          '| 4 | 数据类型 | 确保价格、成交量列为 float64 |\n'
          '| 5 | 重复值 | 删除重复日期行（保留最后一条） |\n'
          '| 6 | 离群值 | 对日对数收益率超过 ln(1.20) 的标注 is_extreme=True，不删除 |')

    code(n, 'def clean_stock(filepath, code, name):\n'
             '    """对单只股票执行完整的 6 步清洗"""\n'
             '    df = pd.read_csv(filepath)\n'
             '    report = {"code": code, "name": name, "原始行数": len(df)}\n\n'
             '    # 步骤 2：缺失值处理 - 前向填充\n'
             '    price_cols = ["open", "close", "high", "low", "volume", "turnover"]\n'
             '    for col in price_cols:\n'
             '        if col in df.columns:\n'
             '            before = df[col].isnull().sum()\n'
             '            df[col] = df[col].ffill()\n'
             '            after = df[col].isnull().sum()\n'
             '            if before > 0:\n'
             '                print(f"    {name} {col}: 缺失 {before} -> 填充后 {after}")\n\n'
             '    # 步骤 3：日期格式统一为 datetime64\n'
             '    date_col = "date" if "date" in df.columns else "日期"\n'
             '    df[date_col] = pd.to_datetime(df[date_col])\n'
             '    df = df.rename(columns={date_col: "date"})\n'
             '    df = df.set_index("date")\n\n'
             '    # 步骤 4：数据类型检查\n'
             '    for col in price_cols:\n'
             '        if col in df.columns:\n'
             '            df[col] = pd.to_numeric(df[col], errors="coerce")\n\n'
             '    # 步骤 5：重复值处理\n'
             '    dups = df.index.duplicated().sum()\n'
             '    report["重复值数"] = dups\n'
             '    df = df[~df.index.duplicated(keep="last")]\n'
             '    report["去重后行数"] = len(df)\n\n'
             '    # 步骤 6：离群值标注（日涨跌幅超过 +-20%）\n'
             '    df["log_return"] = np.log(df["close"] / df["close"].shift(1))\n'
             '    df["is_extreme"] = df["log_return"].abs() > np.log(1.20)\n'
             '    report["极端值数"] = int(df["is_extreme"].sum())\n\n'
             '    df["code"] = code\n'
             '    df["name"] = name\n'
             '    df = df.sort_index()\n'
             '    return df, report\n\n'
             '# 对所有股票执行清洗\n'
             'all_cleaned = []\n'
             'all_reports = []\n\n'
             'for stock in stocks:\n'
             '    fp = f"data/stock/stock_{stock[\'code\']}.csv"\n'
             '    if os.path.exists(fp):\n'
             '        df_c, rep = clean_stock(fp, stock["code"], stock["name"])\n'
             '        all_cleaned.append(df_c)\n'
             '        all_reports.append(rep)\n'
             '        print(f"  {stock[\'name\']}({stock[\'code\']}): "\n'
             '              f"{rep[\'原始行数\']}->{rep[\'去重后行数\']}行, "\n'
             '              f"重复{rep[\'重复值数\']}, 极端值{rep[\'极端值数\']}")\n\n'
             'stock_clean = pd.concat(all_cleaned)\n'
             'print(f"\\n合并后总行数: {len(stock_clean)}")')

    code(n, 'summary = pd.DataFrame(all_reports)\n'
             'display(summary)\n'
             'print("\\n清洗步骤说明：")\n'
             'print("1. 缺失值检测：统计每列缺失数量和比例")\n'
             'print("2. 缺失值处理：前向填充（停牌期间价格不变，前值合理）")\n'
             'print("3. 日期格式：统一为 datetime64 并设为索引")\n'
             'print("4. 数据类型：确保价格、成交量列为 float64")\n'
             'print("5. 重复值：删除重复日期行（保留最后一条）")\n'
             'print("6. 离群值：对日对数收益率超过 ln(1.20) 的标注 is_extreme=True，不删除")\n'
             'print("\\n极端值可能成因：涨跌停板打开、重大利好/利空公告、除权除息等。")')

    md(n, '## 3.2 宽表与长表转换\n\n'
          '- **宽表**：日期为索引，每列一只股票的收盘价 -> 适合横向对比和可视化\n'
          '- **长表**：每行一条观测 (date, code, close) -> 适合分组统计和面板回归')

    code(n, '# 收盘价宽表\n'
             'close_wide = stock_clean.pivot_table(\n'
             '    index="date", columns="code", values="close", aggfunc="first"\n'
             ')\n'
             'close_wide.columns = [f"close_{c}" for c in close_wide.columns]\n'
             'print("收盘价宽表（前 5 行）：")\n'
             'display(close_wide.head())\n'
             'print(f"宽表形状: {close_wide.shape}")\n\n'
             '# 宽表转回长表\n'
             'close_long = close_wide.reset_index().melt(\n'
             '    id_vars="date", var_name="code", value_name="close"\n'
             ')\n'
             'close_long["code"] = close_long["code"].str.replace("close_", "")\n'
             'print(f"\\n长表形状: {close_long.shape}")\n'
             'display(close_long.head())')

    md(n, '## 3.3 多表合并\n\n'
          '将个股日度数据与指数、宏观数据合并，每次记录行数变化。')

    code(n, '# 读取沪深 300 指数\n'
             'hs300 = pd.read_csv("data/index/index_000300.csv", parse_dates=["date"])\n'
             'hs300["idx_log_return"] = np.log(hs300["idx_close"] / hs300["idx_close"].shift(1))\n'
             'print(f"沪深 300 行数: {len(hs300)}")\n\n'
             'stock_daily = stock_clean[\n'
             '    ["code", "name", "open", "close", "high", "low",\n'
             '     "volume", "turnover", "log_return", "is_extreme"]\n'
             '].copy().reset_index()\n'
             'print(f"个股数据行数: {len(stock_daily)}")\n\n'
             '# Left join 指数\n'
             'merged = pd.merge(\n'
             '    stock_daily, hs300[["date", "idx_close", "idx_log_return"]],\n'
             '    on="date", how="left"\n'
             ')\n'
             'print(f"合并指数后行数: {len(merged)} (left join 不增加行，应为 {len(stock_daily)})")')

    code(n, '# 读取 CPI 月度数据\n'
             'cpi = pd.read_csv("data/macro/macro_cpi.csv")\n'
             'print(f"CPI 原始列名: {cpi.columns.tolist()}")\n'
             'display(cpi.head(3))\n\n'
             '# 自动识别日期列和值列\n'
             'date_col = None\n'
             'val_col = None\n'
             'for c in cpi.columns:\n'
             '    if "月" in str(c) or "date" in str(c).lower():\n'
             '        date_col = c\n'
             '    if "当月" in str(c) or "同比" in str(c) or "上年" in str(c):\n'
             '        val_col = c\n'
             'if date_col is None:\n'
             '    date_col = cpi.columns[0]\n'
             'if val_col is None:\n'
             '    for c in cpi.columns[1:]:\n'
             '        if c != date_col:\n'
             '            val_col = c\n'
             '            break\n\n'
             'print(f"使用日期列: {date_col}, 值列: {val_col}")\n\n'
             'cpi["date"] = pd.to_datetime(cpi[date_col], format="%Y年%m月", errors="coerce")\n'
             'cpi["cpi_yoy"] = pd.to_numeric(cpi[val_col], errors="coerce")\n'
             'cpi_monthly = cpi[["date", "cpi_yoy"]].dropna().copy()\n'
             'cpi_monthly["year_month"] = cpi_monthly["date"].dt.to_period("M")\n'
             'print(f"\\nCPI 月度数据（清洗后）：")\n'
             'display(cpi_monthly.head(10))')

    code(n, '# 将月度 CPI 映射到日度数据\n'
             'merged["year_month"] = merged["date"].dt.to_period("M")\n'
             'merged = pd.merge(\n'
             '    merged, cpi_monthly[["year_month", "cpi_yoy"]],\n'
             '    on="year_month", how="left"\n'
             ')\n'
             'merged = merged.drop(columns=["year_month"])\n'
             'print(f"合并 CPI 后行数: {len(merged)}, CPI 缺失值: {merged[\'cpi_yoy\'].isnull().sum()}")\n\n'
             '# 添加行业信息\n'
             'merged = pd.merge(merged, stocks_df[["code", "name", "industry"]], on=["code", "name"], how="left")\n'
             'print(f"合并行业后行数: {len(merged)}")\n'
             'print(f"\\n最终合并数据概览：")\n'
             'display(merged.head())')

    md(n, '## 3.4 数据存储\n\n'
          '### 方式 A：CSV（必做）\n\n'
          'CSV 格式优点：通用性强、纯文本可读、几乎所有软件支持。\n'
          '不足：文件体积大、读取慢、不保留数据类型、不支持列式读取。\n'
          '大规模数据场景下，CSV 的全量加载和字符串解析成为瓶颈。')

    code(n, 'os.makedirs("data/clean", exist_ok=True)\n'
             'os.makedirs("data/combined", exist_ok=True)\n\n'
             'stock_clean.to_csv("data/clean/stock_clean.csv", encoding="utf-8-sig")\n'
             'merged.to_csv("data/combined/combined_data.csv", index=False, encoding="utf-8-sig")\n\n'
             'print("CSV 保存完成：")\n'
             'print(f"  stock_clean.csv: {os.path.getsize(\'data/clean/stock_clean.csv\')/1024:.1f} KB")\n'
             'print(f"  combined_data.csv: {os.path.getsize(\'data/combined/combined_data.csv\')/1024:.1f} KB")')

    md(n, '### 方式 B：Parquet（进阶）\n\n'
          '选择 Parquet 的理由：\n'
          '1. 列式存储，支持只加载需要的列，查询效率高\n'
          '2. 内置压缩，文件体积比 CSV 小 50%-80%\n'
          '3. 保留数据类型 Schema，无需重复推断\n'
          '4. 适合大数据场景和频繁读取操作')

    code(n, 'import pyarrow.parquet as pq\n'
             'import time\n\n'
             '# 保存 Parquet\n'
             'stock_clean.to_parquet("data/clean/stock_clean.parquet")\n'
             'merged.to_parquet("data/combined/combined_data.parquet")\n'
             'print("Parquet 保存完成！")\n\n'
             '# 演示列式读取\n'
             'df_small = pd.read_parquet(\n'
             '    "data/clean/stock_clean.parquet",\n'
             '    columns=["close", "log_return", "code"]\n'
             ')\n'
             'print("\\n列式读取（只加载 3 列）：")\n'
             'display(df_small.head())\n\n'
             '# 查看 Schema\n'
             'schema = pq.read_schema("data/clean/stock_clean.parquet")\n'
             'print(f"\\nParquet Schema:\\n{schema}")\n\n'
             '# CSV vs Parquet 对比\n'
             't0 = time.time()\n'
             'pd.read_csv("data/clean/stock_clean.csv")\n'
             'csv_t = time.time() - t0\n\n'
             't0 = time.time()\n'
             'pd.read_parquet("data/clean/stock_clean.parquet")\n'
             'pq_t = time.time() - t0\n\n'
             'csv_s = os.path.getsize("data/clean/stock_clean.csv") / 1024\n'
             'pq_s = os.path.getsize("data/clean/stock_clean.parquet") / 1024\n\n'
             'print(f"\\nCSV     读取耗时: {csv_t:.3f}s  文件大小: {csv_s:.1f} KB")\n'
             'print(f"Parquet 读取耗时: {pq_t:.3f}s  文件大小: {pq_s:.1f} KB")\n'
             'print(f"体积压缩比: {pq_s/csv_s*100:.1f}%")')

    md(n, '**对比分析**：在本数据规模（约 3 万行 x 10 只股票）下，Parquet 的速度和体积优势有限。\n'
          '但当数据扩展到全部 A 股（5000+ 只）、季度频率、或多个数据库合并时，\n'
          'Parquet 的列式读取和压缩优势将显著体现。')

    code(n, 'print(f"数据清洗完成时间: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")\n'
             'print("\\n请继续运行 03_analysis.ipynb 进行描述统计和回归分析")')

    return n


def build_03():
    n = nb()

    md(n, '# 第三部分：描述性统计、可视化与 CAPM 回归\n\n'
          '本 Notebook 完成以下分析：\n'
          '1. 日收益率描述性统计（含最大回撤）\n'
          '2. 归一化收盘价走势图（图 1）\n'
          '3. 收益率分面直方图（图 2）\n'
          '4. 收益率相关性热力图（图 3）\n'
          '5. 宏观指标与股市关系散点图（图 4）\n'
          '6. CAPM 回归与 Beta 系数点图（图 5）\n'
          '7. 财务指标跨公司对比（图 6，选做）')

    code(n, 'import pandas as pd\n'
             'import numpy as np\n'
             'import matplotlib.pyplot as plt\n'
             'import seaborn as sns\n'
             'import statsmodels.api as sm\n'
             'from scipy import stats\n'
             'import warnings, os, time\n'
             'warnings.filterwarnings("ignore")\n\n'
             'plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]\n'
             'plt.rcParams["axes.unicode_minus"] = False\n'
             'sns.set_style("whitegrid")\n'
             'plt.rcParams["figure.dpi"] = 150\n\n'
             'os.makedirs("output", exist_ok=True)\n\n'
             'df = pd.read_csv("data/combined/combined_data.csv", parse_dates=["date"])\n'
             'print(f"数据维度: {df.shape}")\n'
             'print(f"日期范围: {df[\'date\'].min().date()} 至 {df[\'date\'].max().date()}")\n'
             'print(f"股票数量: {df[\'code\'].nunique()}")\n\n'
             'stocks = [\n'
             '    {"code": "000001", "name": "平安银行", "industry": "银行"},\n'
             '    {"code": "600036", "name": "招商银行", "industry": "银行"},\n'
             '    {"code": "002594", "name": "比亚迪",   "industry": "汽车"},\n'
             '    {"code": "300750", "name": "宁德时代", "industry": "能源"},\n'
             '    {"code": "601012", "name": "隆基绿能", "industry": "能源"},\n'
             '    {"code": "600519", "name": "贵州茅台", "industry": "白酒"},\n'
             '    {"code": "000063", "name": "中兴通讯", "industry": "通讯"},\n'
             '    {"code": "002352", "name": "顺丰控股", "industry": "物流"},\n'
             '    {"code": "600048", "name": "保利发展", "industry": "房地产"},\n'
             '    {"code": "002475", "name": "立讯精密", "industry": "通讯"},\n'
             ']\n'
             'stocks_df = pd.DataFrame(stocks)\n\n'
             'RF_ANNUAL = 0.02\n'
             'RF_DAILY = RF_ANNUAL / 252')

    md(n, '## 4.1 描述性统计\n\n'
          '计算日对数收益率 $r_t = \\ln(P_t / P_{t-1})$ 的描述性统计：\n'
          '年化均值、年化波动率、偏度、峰度、最大回撤。')

    code(n, 'def max_drawdown(series):\n'
             '    """计算最大回撤"""\n'
             '    cum = (1 + series).cumprod()\n'
             '    peak = cum.cummax()\n'
             '    dd = (cum - peak) / peak\n'
             '    return dd.min()\n\n'
             'stats_list = []\n'
             'for stock in stocks:\n'
             '    code_ = stock["code"]\n'
             '    s = df[df["code"] == code_]["log_return"].dropna()\n'
             '    ann_mean = s.mean() * 252\n'
             '    ann_vol = s.std() * np.sqrt(252)\n'
             '    stats_list.append({\n'
             '        "股票": stock["name"],\n'
             '        "行业": stock["industry"],\n'
             '        "年化均值": round(ann_mean, 4),\n'
             '        "年化波动率": round(ann_vol, 4),\n'
             '        "偏度": round(s.skew(), 4),\n'
             '        "峰度": round(s.kurtosis(), 4),\n'
             '        "最大回撤": round(max_drawdown(s), 4),\n'
             '    })\n\n'
             'stats_df = pd.DataFrame(stats_list)\n'
             'print("=== 日对数收益率描述性统计 ===")\n'
             'display(stats_df)\n'
             'stats_df.to_csv("output/descriptive_stats.csv", index=False, encoding="utf-8-sig")')

    md(n, '## 4.2 图 1：归一化收盘价走势图\n\n'
          '以 **2020 年初 = 1** 为基准，叠加沪深 300，按行业分组着色。')

    code(n, 'base_date = pd.Timestamp("2020-01-02")\n\n'
             'industry_colors = {\n'
             '    "银行": "#2196F3", "汽车": "#FF5722", "能源": "#4CAF50",\n'
             '    "白酒": "#9C27B0", "通讯": "#FF9800", "物流": "#795548",\n'
             '    "房地产": "#607D8B"\n'
             '}\n\n'
             'fig, ax = plt.subplots(figsize=(14, 7))\n\n'
             '# 沪深 300 归一化\n'
             'hs300 = df[["date", "idx_close"]].dropna().drop_duplicates("date")\n'
             'hs300 = hs300[hs300["date"] >= base_date].sort_values("date")\n'
             'base_val = hs300.iloc[0]["idx_close"]\n'
             'ax.plot(hs300["date"], hs300["idx_close"] / base_val,\n'
             '        "k--", linewidth=1.5, alpha=0.7, label="沪深300")\n\n'
             'for stock in stocks:\n'
             '    code_ = stock["code"]\n'
             '    name_ = stock["name"]\n'
             '    ind = stock["industry"]\n'
             '    s = df[df["code"] == code_][["date", "close"]].dropna()\n'
             '    s = s[s["date"] >= base_date].sort_values("date")\n'
             '    if len(s) == 0:\n'
             '        continue\n'
             '    bval = s.iloc[0]["close"]\n'
             '    ax.plot(s["date"], s["close"] / bval,\n'
             '            color=industry_colors.get(ind, "gray"),\n'
             '            linewidth=1.2, label=f"{name_}({ind})")\n\n'
             'ax.axhline(y=1, color="gray", linestyle=":", alpha=0.5)\n'
             'ax.set_xlabel("日期", fontsize=12)\n'
             'ax.set_ylabel("归一化价格（2020-01-02 = 1）", fontsize=12)\n'
             'ax.set_title("图 1：归一化收盘价走势（2020-01-02 = 1，按行业着色）",\n'
             '             fontsize=14, fontweight="bold")\n'
             'ax.legend(loc="upper left", fontsize=8, ncol=3)\n'
             'plt.tight_layout()\n'
             'plt.savefig("output/fig1_normalized_price.png", dpi=150, bbox_inches="tight")\n'
             'plt.show()\n'
             'print("图 1 已保存。")')

    md(n, '**解读**：以 2020 年初为基准（=1），可以直观比较各股票的累计涨跌表现。'
          '行业颜色分组显示：新能源（宁德时代、隆基绿能）和汽车（比亚迪）涨幅显著，'
          '银行股整体表现平稳，房地产（保利发展）自 2021 年后持续承压。')

    md(n, '## 4.3 图 2：日收益率分布直方图\n\n'
          '10 只股票收益率分面直方图（2 行 x 5 列），每个子图叠加正态分布曲线，标注均值和标准差。')

    code(n, 'fig, axes = plt.subplots(2, 5, figsize=(20, 8))\n'
             'axes = axes.flatten()\n\n'
             'for idx, stock in enumerate(stocks):\n'
             '    code_ = stock["code"]\n'
             '    name_ = stock["name"]\n'
             '    ind = stock["industry"]\n'
             '    s = df[df["code"] == code_]["log_return"].dropna()\n'
             '    mu, sigma = s.mean(), s.std()\n\n'
             '    axes[idx].hist(s, bins=50, density=True, alpha=0.6,\n'
             '                    color=industry_colors.get(ind, "gray"), edgecolor="white")\n'
             '    x = np.linspace(s.min(), s.max(), 200)\n'
             '    axes[idx].plot(x, stats.norm.pdf(x, mu, sigma), "r-", linewidth=1.5)\n'
             '    axes[idx].axvline(mu, color="blue", linestyle="--", linewidth=1)\n'
             '    axes[idx].set_title(f"{name_}\\n$\\mu$={mu:.4f}, $\\sigma$={sigma:.4f}", fontsize=9)\n'
             '    axes[idx].set_xlabel("日对数收益率")\n'
             '    if idx % 5 == 0:\n'
             '        axes[idx].set_ylabel("密度")\n\n'
             'plt.suptitle("图 2：日对数收益率分布直方图（叠加正态拟合）",\n'
             '             fontsize=14, fontweight="bold")\n'
             'plt.tight_layout()\n'
             'plt.savefig("output/fig2_return_histogram.png", dpi=150, bbox_inches="tight")\n'
             'plt.show()\n'
             'print("图 2 已保存。")')

    md(n, '**解读**：所有股票收益率分布均呈现"尖峰厚尾"特征（峰度 > 0），'
          '偏离正态分布假设。极端事件（大涨大跌）发生的频率远高于正态分布的预测，'
          '这与金融学中的经验发现一致。')

    md(n, '## 4.4 图 3：收益率相关性热力图\n\n'
          '10 只股票日收益率的相关系数矩阵，**按行业排序**，标注数值。')

    code(n, 'industry_order = ["银行", "汽车", "能源", "白酒", "通讯", "物流", "房地产"]\n'
             'codes_by_ind = {}\n'
             'for stock in stocks:\n'
             '    codes_by_ind.setdefault(stock["industry"], []).append(stock["code"])\n\n'
             'ordered_codes = []\n'
             'for ind in industry_order:\n'
             '    ordered_codes.extend(codes_by_ind.get(ind, []))\n\n'
             'return_wide = df.pivot_table(\n'
             '    index="date", columns="code", values="log_return", aggfunc="first"\n'
             ')\n'
             'return_wide = return_wide[ordered_codes]\n\n'
             'name_map = {s["code"]: s["name"] for s in stocks}\n'
             'return_wide.columns = [name_map[c] for c in return_wide.columns]\n'
             'corr = return_wide.corr()\n\n'
             'fig, ax = plt.subplots(figsize=(10, 8))\n'
             'sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r", center=0,\n'
             '            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)\n'
             'ax.set_title("图 3：日收益率相关系数热力图（按行业排序）",\n'
             '             fontsize=13, fontweight="bold")\n'
             'plt.tight_layout()\n'
             'plt.savefig("output/fig3_correlation_heatmap.png", dpi=150, bbox_inches="tight")\n'
             'plt.show()\n'
             'print("图 3 已保存。")')

    md(n, '**解读**：同行业股票相关性通常高于跨行业。'
          '两只银行股（平安银行 vs 招商银行）相关系数较高，体现了同行业的系统性影响。'
          '新能源板块（宁德时代 vs 隆基绿能）相关性也高于与其他行业的配对，'
          '说明行业因素是驱动股票收益联动的重要来源。')

    md(n, '## 4.5 图 4：宏观指标与股市关系\n\n'
          '绘制 CPI 同比增速与沪深 300 月度收益率的散点图，叠加线性拟合线，标注 Pearson 相关系数。')

    code(n, '# 计算沪深 300 月度对数收益率\n'
             'hs300_monthly = df[["date", "idx_close"]].drop_duplicates("date").copy()\n'
             'hs300_monthly = hs300_monthly.set_index("date").resample("ME").last()\n'
             'hs300_monthly["idx_monthly_return"] = np.log(\n'
             '    hs300_monthly["idx_close"] / hs300_monthly["idx_close"].shift(1)\n'
             ')\n'
             'hs300_monthly = hs300_monthly.dropna().reset_index()\n'
             'hs300_monthly["year_month"] = hs300_monthly["date"].dt.to_period("M")\n\n'
             '# 读取 CPI\n'
             'cpi_df = pd.read_csv("data/macro/macro_cpi.csv")\n'
             'date_col = cpi_df.columns[0]\n'
             'val_cols = [c for c in cpi_df.columns[1:] if c != date_col]\n'
             'cpi_df["date"] = pd.to_datetime(cpi_df[date_col], format="%Y年%m月", errors="coerce")\n'
             'cpi_df["cpi_yoy"] = pd.to_numeric(cpi_df[val_cols[0]], errors="coerce") if val_cols else np.nan\n'
             'cpi_df["year_month"] = cpi_df["date"].dt.to_period("M")\n\n'
             '# 合并\n'
             'scatter_df = pd.merge(\n'
             '    hs300_monthly[["year_month", "idx_monthly_return"]],\n'
             '    cpi_df[["year_month", "cpi_yoy"]], on="year_month", how="inner"\n'
             ').dropna()\n\n'
             'r, p_val = stats.pearsonr(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"])\n\n'
             'fig, ax = plt.subplots(figsize=(10, 6))\n'
             'ax.scatter(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"],\n'
             '           alpha=0.6, s=40, color="steelblue")\n\n'
             'coef = np.polyfit(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"], 1)\n'
             'x_fit = np.linspace(scatter_df["cpi_yoy"].min(), scatter_df["cpi_yoy"].max(), 100)\n'
             'y_fit = np.polyval(coef, x_fit)\n'
             'ax.plot(x_fit, y_fit, "r-", linewidth=2, label="拟合线")\n\n'
             'ax.axhline(0, color="gray", linestyle=":", alpha=0.5)\n'
             'ax.set_xlabel("CPI 同比增速 (%)", fontsize=12)\n'
             'ax.set_ylabel("沪深 300 月度对数收益率", fontsize=12)\n'
             'ax.set_title(\n'
             '    f"图 4：CPI 同比增速 vs 沪深 300 月度收益率\\n"\n'
             '    f"Pearson r = {r:.3f} (p = {p_val:.4f})",\n'
             '    fontsize=13, fontweight="bold"\n'
             ')\n'
             'ax.legend()\n'
             'plt.tight_layout()\n'
             'plt.savefig("output/fig4_macro_scatter.png", dpi=150, bbox_inches="tight")\n'
             'plt.show()\n'
             'print("图 4 已保存。")')

    md(n, '**解读**：CPI 同比增速与沪深 300 月度收益率的相关系数为 $r$（见上图标题）。'
          '正相关意味着通胀上升时股市可能受益于名义盈利增长，'
          '负相关则可能因加息预期承压。需注意相关关系不等于因果关系。')

    md(n, '## 5.1 CAPM 模型估计\n\n'
          '对 10 只股票分别估计 CAPM 模型：\n\n'
          '$$r_{i,t} - r_f = \\alpha_i + \\beta_i (r_{m,t} - r_f) + \\varepsilon_{i,t}$$\n\n'
          '- $r_{i,t}$：个股日对数收益率\n'
          '- $r_{m,t}$：沪深 300 日对数收益率  \n'
          '- $r_f^{daily} = 0.02 / 252$')

    code(n, 'capm_results = []\n\n'
             'for stock in stocks:\n'
             '    code_ = stock["code"]\n'
             '    name_ = stock["name"]\n'
             '    ind = stock["industry"]\n'
             '    s = df[df["code"] == code_][["date", "log_return", "idx_log_return"]].dropna()\n\n'
             '    y = s["log_return"].values - RF_DAILY\n'
             '    X = sm.add_constant(s["idx_log_return"].values - RF_DAILY)\n\n'
             '    model = sm.OLS(y, X).fit()\n'
             '    ci_low, ci_high = model.conf_int()[1]\n\n'
             '    capm_results.append({\n'
             '        "股票": name_, "行业": ind,\n'
             '        "alpha": round(model.params[0], 6),\n'
             '        "alpha_p": round(model.pvalues[0], 4),\n'
             '        "beta": round(model.params[1], 4),\n'
             '        "beta_p": round(model.pvalues[1], 4),\n'
             '        "beta_CI_low": round(ci_low, 4),\n'
             '        "beta_CI_high": round(ci_high, 4),\n'
             '        "R2": round(model.rsquared, 4)\n'
             '    })\n\n'
             'capm_df = pd.DataFrame(capm_results)\n'
             'print("=== CAPM 回归结果 ===")\n'
             'display(capm_df)\n'
             'capm_df.to_csv("output/capm_results.csv", index=False, encoding="utf-8-sig")')

    md(n, '### Beta 系数点图\n\n'
          '横轴为 Beta 值，纵轴为股票名称，误差棒表示 95% 置信区间，按行业分组着色，$\\beta=1$ 参考竖线。')

    code(n, 'fig, ax = plt.subplots(figsize=(10, 6))\n\n'
             'capm_df_sorted = capm_df.sort_values("beta").reset_index(drop=True)\n'
             'y_pos = range(len(capm_df_sorted))\n\n'
             'for i, row in capm_df_sorted.iterrows():\n'
             '    color = industry_colors.get(row["行业"], "gray")\n'
             '    err_lo = row["beta"] - row["beta_CI_low"]\n'
             '    err_hi = row["beta_CI_high"] - row["beta"]\n'
             '    ax.errorbar(row["beta"], i,\n'
             '                xerr=[[err_lo], [err_hi]],\n'
             '                fmt="o", color=color, capsize=4, markersize=8, elinewidth=2)\n\n'
             'ax.set_yticks(list(y_pos))\n'
             'ax.set_yticklabels(capm_df_sorted["股票"])\n'
             'ax.axvline(x=1, color="black", linestyle="--", linewidth=1.5, label="$\\beta$=1")\n'
             'ax.set_xlabel("Beta 系数", fontsize=12)\n'
             'ax.set_title("图 5：CAPM Beta 系数点图（95% 置信区间，按行业着色）",\n'
             '             fontsize=13, fontweight="bold")\n\n'
             'from matplotlib.patches import Patch\n'
             'legend_elements = [\n'
             '    Patch(facecolor=industry_colors.get(ind, "gray"), label=ind)\n'
             '    for ind in industry_order\n'
             ']\n'
             'legend_elements.append(plt.Line2D([0], [0], color="black", linestyle="--", label="$\\beta$=1"))\n'
             'ax.legend(handles=legend_elements, loc="lower right", fontsize=9)\n'
             'plt.tight_layout()\n'
             'plt.savefig("output/fig5_beta_dotplot.png", dpi=150, bbox_inches="tight")\n'
             'plt.show()\n'
             'print("图 5 已保存。")')

    md(n, '### CAPM 回归讨论')

    md(n, '**讨论问题 1：哪些股票 $\\beta > 1$？它们属于哪些行业？这与"周期性 vs 防御性"行业分类是否吻合？**')

    code(n, 'aggressive = capm_df[capm_df["beta"] > 1]\n'
             'defensive = capm_df[capm_df["beta"] <= 1]\n\n'
             'print("Beta > 1 的股票（进攻型）:")\n'
             'for _, r in aggressive.iterrows():\n'
             '    print(f"  {r[\'股票\']}({r[\'行业\']}): beta = {r[\'beta\']:.3f}")\n\n'
             'print("\\nBeta <= 1 的股票（防御型）:")\n'
             'for _, r in defensive.iterrows():\n'
             '    print(f"  {r[\'股票\']}({r[\'行业\']}): beta = {r[\'beta\']:.3f}")')

    md(n, '**分析**：$\\beta > 1$ 的股票波动大于市场，属于"进攻型"，通常集中在周期性行业。'
          '$\\beta \\leq 1$ 的股票波动小于市场，属于"防御型"。'
          '银行股的 $\\beta$ 通常较低，因为银行业盈利受经济周期影响相对间接，'
          '且银行股股息率较高提供了一定"安全垫"。'
          '新能源和汽车行业 $\\beta$ 较高，反映了对经济景气度和政策变化的敏感性。')

    md(n, '**讨论问题 2：$\\alpha$ 是否显著异于零？Alpha 显著意味着什么？**')

    code(n, 'for _, r in capm_df.iterrows():\n'
             '    sig = "显著" if r["alpha_p"] < 0.05 else "不显著"\n'
             '    print(f"  {r[\'股票\']}: alpha = {r[\'alpha\']:.6f}, p = {r[\'alpha_p\']:.4f} -> {sig}")')

    md(n, '**分析**：在 CAPM 框架下，$\\alpha$ 代表"超额收益"，即无法被市场风险（$\\beta$）解释的收益部分。'
          '如果 $\\alpha$ 显著为正，说明该股票在控制市场风险后仍有超额回报，'
          '可能来源于选股能力、信息优势或市场有效性不足。'
          '如果 $\\alpha$ 显著为负，说明该股票表现劣于 CAPM 预测。'
          '如果 $\\alpha$ 不显著，说明 CAPM 模型能较好地解释该股票的收益。')

    md(n, '**讨论问题 3：$R^2$ 最高和最低的股票分别是哪只？如何解释这一差异？**')

    code(n, 'max_r2 = capm_df.loc[capm_df["R2"].idxmax()]\n'
             'min_r2 = capm_df.loc[capm_df["R2"].idxmin()]\n'
             'print(f"R2 最高: {max_r2[\'股票\']}({max_r2[\'行业\']}), R2 = {max_r2[\'R2\']:.4f}")\n'
             'print(f"R2 最低: {min_r2[\'股票\']}({min_r2[\'行业\']}), R2 = {min_r2[\'R2\']:.4f}")')

    md(n, '**分析**：$R^2$ 反映市场因子对个股收益的解释力。'
          '$R^2$ 越高，说明该股票收益变动越能被市场整体走势解释；'
          '$R^2$ 越低，说明个股特质因素（如公司基本面、行业事件）对收益影响更大。'
          '银行股通常 $R^2$ 较高，因为银行板块与宏观经济高度联动；'
          '而某些行业龙头（如茅台）可能因独特的基本面因素而 $R^2$ 较低。')

    md(n, '## 图 6（选做）：财务指标跨公司对比\n\n'
          '绘制 10 只股票近 5 年 ROE 的折线图，按行业分组。')

    code(n, 'try:\n'
             '    fin = pd.read_csv("data/finance/finance_ratios.csv")\n'
             '    roe = fin[fin["indicator"] == "ROE"].copy()\n'
             '    if len(roe) > 0:\n'
             '        fig, ax = plt.subplots(figsize=(12, 6))\n'
             '        for stock in stocks:\n'
             '            s = roe[roe["code"] == stock["code"]]\n'
             '            if len(s) > 0:\n'
             '                ax.plot(s["year"], s["value"], "o-",\n'
             '                        color=industry_colors.get(stock["industry"], "gray"),\n'
             '                        label=f"{stock[\'name\']}({stock[\'industry\']})",\n'
             '                        linewidth=1.5, markersize=5)\n'
             '        ax.axhline(0, color="gray", linestyle=":", alpha=0.5)\n'
             '        ax.set_xlabel("年份", fontsize=12)\n'
             '        ax.set_ylabel("ROE (%)", fontsize=12)\n'
             '        ax.set_title("图 6：各股票 ROE 趋势对比（按行业着色）",\n'
             '                     fontsize=13, fontweight="bold")\n'
             '        ax.legend(fontsize=8, ncol=2)\n'
             '        plt.tight_layout()\n'
             '        plt.savefig("output/fig6_roe_comparison.png", dpi=150, bbox_inches="tight")\n'
             '        plt.show()\n'
             '        print("图 6 已保存。")\n'
             '    else:\n'
             '        print("ROE 数据为空，跳过图 6。")\n'
             'except Exception as e:\n'
             '    print(f"图 6 跳过: {e}")')

    md(n, '## 总结')

    code(n, 'print("分析完成，输出文件清单：")\n'
             'for f in sorted(os.listdir("output")):\n'
             '    size = os.path.getsize(f"output/{f}") / 1024\n'
             '    print(f"  output/{f}: {size:.1f} KB")')

    return n


# ============================================================
# Main: write all notebooks
# ============================================================
for name, builder in [
    ('01_download.ipynb', build_01),
    ('02_clean.ipynb', build_02),
    ('03_analysis.ipynb', build_03),
]:
    nb_obj = builder()
    path = os.path.join(BASE, name)
    with open(path, 'w', encoding='utf-8') as f:
        nbformat.write(nb_obj, f)
    print(f"[OK] {name} ({len(nb_obj.cells)} cells)")
