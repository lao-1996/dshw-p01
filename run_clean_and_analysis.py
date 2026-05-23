"""
02_clean + 03_analysis 替代脚本
绕过 notebook JSON 格式问题，直接完成数据清洗、合并、描述统计、可视化、CAPM 回归
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # 无头模式，不需要显示器
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
import warnings, os, time
from datetime import datetime

warnings.filterwarnings("ignore")
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 150

# ============================================================
# 配置
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
stocks_df = pd.DataFrame(stocks)
RF_ANNUAL = 0.02
RF_DAILY = RF_ANNUAL / 252

industry_colors = {
    "银行": "#2196F3", "汽车": "#FF5722", "能源": "#4CAF50",
    "白酒": "#9C27B0", "通讯": "#FF9800", "物流": "#795548", "房地产": "#607D8B"
}
industry_order = ["银行", "汽车", "能源", "白酒", "通讯", "物流", "房地产"]

os.makedirs("data/clean", exist_ok=True)
os.makedirs("data/combined", exist_ok=True)
os.makedirs("output", exist_ok=True)

print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================
# 第一部分：数据清洗 (02_clean)
# ============================================================
print("\n===== 第一部分：数据清洗 =====")

def clean_stock(df, code, name):
    """对单只股票执行 6 步清洗"""
    report = {"code": code, "name": name, "原始行数": len(df)}

    # 步骤 2：缺失值处理 - 前向填充
    price_cols = ["open", "close", "high", "low", "volume", "turnover"]
    for col in price_cols:
        if col in df.columns:
            df[col] = df[col].ffill()

    # 步骤 3：日期格式统一为 datetime64
    date_col = "date" if "date" in df.columns else "日期"
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.rename(columns={date_col: "date"})
    df = df.set_index("date")

    # 步骤 4：数据类型检查
    for col in price_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 步骤 5：重复值处理
    dups = df.index.duplicated().sum()
    report["重复值数"] = int(dups)
    df = df[~df.index.duplicated(keep="last")]
    report["去重后行数"] = len(df)

    # 步骤 6：离群值标注
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df["is_extreme"] = df["log_return"].abs() > np.log(1.20)
    report["极端值数"] = int(df["is_extreme"].sum())

    df["code"] = str(code).zfill(6)
    df["name"] = name
    df = df.sort_index()
    return df, report

# 清洗所有股票
all_cleaned = []
all_reports = []

for stock in stocks:
    fp = f"data/stock/stock_{stock['code']}.csv"
    if os.path.exists(fp):
        df_raw = pd.read_csv(fp)
        df_c, rep = clean_stock(df_raw, stock["code"], stock["name"])
        all_cleaned.append(df_c)
        all_reports.append(rep)
        print(f"  {stock['name']}({stock['code']}): "
              f"{rep['原始行数']}->{rep['去重后行数']}行, "
              f"重复{rep['重复值数']}, 极端值{rep['极端值数']}")
    else:
        print(f"  警告: {fp} 不存在，跳过")

stock_clean = pd.concat(all_cleaned)
print(f"合并后总行数: {len(stock_clean)}")

# 保存清洗后数据
stock_clean.to_csv("data/clean/stock_clean.csv", encoding="utf-8-sig")
print("stock_clean.csv 已保存")

# ---- 宽表/长表转换演示 ----
close_wide = stock_clean.pivot_table(
    index="date", columns="code", values="close", aggfunc="first"
)
close_wide.columns = [f"close_{c}" for c in close_wide.columns]
close_long = close_wide.reset_index().melt(
    id_vars="date", var_name="code", value_name="close"
)
close_long["code"] = close_long["code"].str.replace("close_", "")
print(f"宽表形状: {close_wide.shape}, 长表形状: {close_long.shape}")

# ---- 多表合并 ----
# 指数：读取后计算 idx_log_return，再把 close 重命名为 idx_close
hs300 = pd.read_csv("data/index/index_000300.csv", parse_dates=["date"])
hs300 = hs300.sort_values("date").reset_index(drop=True)
hs300["idx_log_return"] = np.log(hs300["close"] / hs300["close"].shift(1))
hs300["idx_close"] = hs300["close"]
hs300 = hs300[["date", "idx_close", "idx_log_return"]].copy()

stock_daily = stock_clean[
    ["code", "name", "open", "close", "high", "low",
     "volume", "turnover", "log_return", "is_extreme"]
].copy().reset_index()

merged = pd.merge(
    stock_daily,
    hs300[["date", "idx_close", "idx_log_return"]],
    on="date", how="left"
)
print(f"合并指数后行数: {len(merged)}")

# CPI
cpi = pd.read_csv("data/macro/macro_cpi.csv")
date_col = None
val_col = None
for c in cpi.columns:
    if "月" in str(c) or "date" in str(c).lower():
        date_col = c
    if "今值" in str(c) or "当月" in str(c) or "cpi" in str(c).lower():
        val_col = c
if date_col is None:
    date_col = cpi.columns[0]
if val_col is None:
    for c in cpi.columns[1:]:
        if c != date_col:
            val_col = c
            break

cpi["date"] = pd.to_datetime(cpi[date_col], errors="coerce")
cpi["cpi_yoy"] = pd.to_numeric(cpi[val_col], errors="coerce")
cpi_monthly = cpi[["date", "cpi_yoy"]].dropna().copy()
cpi_monthly["year_month"] = cpi_monthly["date"].dt.to_period("M")

merged["year_month"] = merged["date"].dt.to_period("M")
merged = pd.merge(
    merged, cpi_monthly[["year_month", "cpi_yoy"]],
    on="year_month", how="left"
)
merged = merged.drop(columns=["year_month"])

# 行业信息
merged = pd.merge(merged, stocks_df[["code", "name", "industry"]],
                  on=["code", "name"], how="left")
print(f"最终合并数据行数: {len(merged)}")

# 保存
merged.to_csv("data/combined/combined_data.csv", index=False, encoding="utf-8-sig")
stock_clean.to_csv("data/clean/stock_clean.csv", encoding="utf-8-sig")
stock_clean.to_parquet("data/clean/stock_clean.parquet")
merged.to_parquet("data/combined/combined_data.parquet")
print("清洗完成，CSV + Parquet 已保存")

# ============================================================
# 第二部分：描述统计、可视化、CAPM (03_analysis)
# ============================================================
print("\n===== 第二部分：描述统计与可视化 =====")

df = merged.copy()
df["date"] = pd.to_datetime(df["date"])
print(f"数据维度: {df.shape}")
print(f"日期范围: {df['date'].min().date()} 至 {df['date'].max().date()}")

# ----- 4.1 描述性统计 -----
def max_drawdown(series):
    cum = (1 + series).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    return dd.min()

stats_list = []
for stock in stocks:
    code_ = stock["code"]
    s = df[df["code"] == code_]["log_return"].dropna()
    if len(s) < 10:
        print(f"  警告: {stock['name']} 有效数据不足 ({len(s)} 行)，跳过")
        stats_list.append({
            "股票": stock["name"],
            "行业": stock["industry"],
            "年化均值": np.nan, "年化波动率": np.nan,
            "偏度": np.nan, "峰度": np.nan, "最大回撤": np.nan,
        })
        continue
    ann_mean = s.mean() * 252
    ann_vol = s.std() * np.sqrt(252)
    stats_list.append({
        "股票": stock["name"],
        "行业": stock["industry"],
        "年化均值": round(ann_mean, 4),
        "年化波动率": round(ann_vol, 4),
        "偏度": round(s.skew(), 4),
        "峰度": round(s.kurtosis(), 4),
        "最大回撤": round(max_drawdown(s), 4),
    })

stats_df = pd.DataFrame(stats_list)
print("\n=== 日对数收益率描述性统计 ===")
print(stats_df.to_string(index=False))
stats_df.to_csv("output/descriptive_stats.csv", index=False, encoding="utf-8-sig")
print("descriptive_stats.csv 已保存")

# ----- 图 1：归一化收盘价走势图 -----
base_date = pd.Timestamp("2020-01-02")
fig, ax = plt.subplots(figsize=(14, 7))

# 沪深300
hs300_plot = df[["date", "idx_close"]].dropna().drop_duplicates("date")
hs300_plot = hs300_plot[hs300_plot["date"] >= base_date].sort_values("date")
if len(hs300_plot) > 0:
    base_val = hs300_plot.iloc[0]["idx_close"]
    ax.plot(hs300_plot["date"], hs300_plot["idx_close"] / base_val,
            "k--", linewidth=1.5, alpha=0.7, label="沪深300")

for stock in stocks:
    code_ = stock["code"]
    name_ = stock["name"]
    ind = stock["industry"]
    s = df[df["code"] == code_][["date", "close"]].dropna()
    s = s[s["date"] >= base_date].sort_values("date")
    if len(s) == 0:
        continue
    bval = s.iloc[0]["close"]
    ax.plot(s["date"], s["close"] / bval,
            color=industry_colors.get(ind, "gray"),
            linewidth=1.2, label=f"{name_}({ind})")

ax.axhline(y=1, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("日期", fontsize=12)
ax.set_ylabel("归一化价格（2020-01-02 = 1）", fontsize=12)
ax.set_title("图 1：归一化收盘价走势（2020-01-02 = 1，按行业着色）",
             fontsize=14, fontweight="bold")
ax.legend(loc="upper left", fontsize=8, ncol=3)
plt.tight_layout()
plt.savefig("output/fig1_normalized_price.png", dpi=150, bbox_inches="tight")
plt.close()
print("图 1 已保存")

# ----- 图 2：收益率分布直方图 -----
fig, axes = plt.subplots(2, 5, figsize=(20, 8))
axes = axes.flatten()

for idx, stock in enumerate(stocks):
    code_ = stock["code"]
    name_ = stock["name"]
    ind = stock["industry"]
    s = df[df["code"] == code_]["log_return"].dropna()
    if len(s) < 5:
        axes[idx].set_title(f"{name_}\n数据不足")
        continue
    mu, sigma = s.mean(), s.std()
    axes[idx].hist(s, bins=50, density=True, alpha=0.6,
                    color=industry_colors.get(ind, "gray"), edgecolor="white")
    x = np.linspace(s.min(), s.max(), 200)
    axes[idx].plot(x, stats.norm.pdf(x, mu, sigma), "r-", linewidth=1.5)
    axes[idx].axvline(mu, color="blue", linestyle="--", linewidth=1)
    axes[idx].set_title(f"{name_}\nμ={mu:.4f}, σ={sigma:.4f}", fontsize=9)
    axes[idx].set_xlabel("日对数收益率")
    if idx % 5 == 0:
        axes[idx].set_ylabel("密度")

plt.suptitle("图 2：日对数收益率分布直方图（叠加正态拟合）",
             fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("output/fig2_return_histogram.png", dpi=150, bbox_inches="tight")
plt.close()
print("图 2 已保存")

# ----- 图 3：收益率相关性热力图 -----
codes_by_ind = {}
for stock in stocks:
    codes_by_ind.setdefault(stock["industry"], []).append(stock["code"])
ordered_codes = []
for ind in industry_order:
    ordered_codes.extend(codes_by_ind.get(ind, []))

return_wide = df.pivot_table(
    index="date", columns="code", values="log_return", aggfunc="first"
)
# 只保留存在的列
ordered_codes = [c for c in ordered_codes if c in return_wide.columns]
return_wide = return_wide[ordered_codes]

name_map = {s["code"]: s["name"] for s in stocks}
return_wide.columns = [name_map.get(c, c) for c in return_wide.columns]
corr = return_wide.corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r", center=0,
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title("图 3：日收益率相关系数热力图（按行业排序）",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("output/fig3_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("图 3 已保存")

# ----- 图 4：CPI vs 沪深300 散点图 -----
hs300_monthly = df[["date", "idx_close"]].drop_duplicates("date").copy()
hs300_monthly = hs300_monthly.set_index("date").resample("ME").last()
hs300_monthly["idx_monthly_return"] = np.log(
    hs300_monthly["idx_close"] / hs300_monthly["idx_close"].shift(1)
)
hs300_monthly = hs300_monthly.dropna().reset_index()
hs300_monthly["year_month"] = hs300_monthly["date"].dt.to_period("M")

scatter_df = pd.merge(
    hs300_monthly[["year_month", "idx_monthly_return"]],
    cpi_monthly[["year_month", "cpi_yoy"]], on="year_month", how="inner"
).dropna()

if len(scatter_df) > 2:
    r, p_val = stats.pearsonr(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"])
else:
    r, p_val = np.nan, np.nan

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"],
           alpha=0.6, s=40, color="steelblue")
if len(scatter_df) > 2:
    coef = np.polyfit(scatter_df["cpi_yoy"], scatter_df["idx_monthly_return"], 1)
    x_fit = np.linspace(scatter_df["cpi_yoy"].min(), scatter_df["cpi_yoy"].max(), 100)
    y_fit = np.polyval(coef, x_fit)
    ax.plot(x_fit, y_fit, "r-", linewidth=2, label="拟合线")

ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
ax.set_xlabel("CPI 同比增速 (%)", fontsize=12)
ax.set_ylabel("沪深 300 月度对数收益率", fontsize=12)
title_str = f"图 4：CPI 同比增速 vs 沪深 300 月度收益率\nPearson r = {r:.3f} (p = {p_val:.4f})" if len(scatter_df) > 2 else "图 4：CPI 同比增速 vs 沪深 300 月度收益率"
ax.set_title(title_str, fontsize=13, fontweight="bold")
ax.legend()
plt.tight_layout()
plt.savefig("output/fig4_macro_scatter.png", dpi=150, bbox_inches="tight")
plt.close()
print("图 4 已保存")

# ----- CAPM 回归 -----
print("\n===== CAPM 回归 =====")
capm_results = []

for stock in stocks:
    code_ = stock["code"]
    name_ = stock["name"]
    ind = stock["industry"]
    s = df[(df["code"] == code_) & (df["idx_log_return"].notna())][["log_return", "idx_log_return"]].dropna()
    if len(s) < 10:
        print(f"  {name_}: 数据不足，跳过")
        continue

    y = s["log_return"].values - RF_DAILY
    X = sm.add_constant(s["idx_log_return"].values - RF_DAILY)
    model = sm.OLS(y, X).fit()
    ci = model.conf_int()
    ci_low, ci_high = ci[1]  # beta 的 95% CI

    capm_results.append({
        "股票": name_, "行业": ind,
        "alpha": round(model.params[0], 6),
        "alpha_p": round(model.pvalues[0], 4),
        "beta": round(model.params[1], 4),
        "beta_p": round(model.pvalues[1], 4),
        "beta_CI_low": round(ci_low, 4),
        "beta_CI_high": round(ci_high, 4),
        "R2": round(model.rsquared, 4)
    })

capm_df = pd.DataFrame(capm_results)
print("=== CAPM 回归结果 ===")
print(capm_df.to_string(index=False))
capm_df.to_csv("output/capm_results.csv", index=False, encoding="utf-8-sig")
print("capm_results.csv 已保存")

# ----- 图 5：Beta 点图 -----
fig, ax = plt.subplots(figsize=(10, 6))
capm_sorted = capm_df.sort_values("beta").reset_index(drop=True)
y_pos = range(len(capm_sorted))

for i, row in capm_sorted.iterrows():
    color = industry_colors.get(row["行业"], "gray")
    err_lo = row["beta"] - row["beta_CI_low"]
    err_hi = row["beta_CI_high"] - row["beta"]
    ax.errorbar(row["beta"], i,
                xerr=[[err_lo], [err_hi]],
                fmt="o", color=color, capsize=4, markersize=8, elinewidth=2)

ax.set_yticks(list(y_pos))
ax.set_yticklabels(capm_sorted["股票"])
ax.axvline(x=1, color="black", linestyle="--", linewidth=1.5, label="β=1")
ax.set_xlabel("Beta 系数", fontsize=12)
ax.set_title("图 5：CAPM Beta 系数点图（95% 置信区间，按行业着色）",
             fontsize=13, fontweight="bold")

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=industry_colors.get(ind, "gray"), label=ind)
    for ind in industry_order if ind in capm_df["行业"].values
]
legend_elements.append(plt.Line2D([0], [0], color="black", linestyle="--", label="β=1"))
ax.legend(handles=legend_elements, loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig("output/fig5_beta_dotplot.png", dpi=150, bbox_inches="tight")
plt.close()
print("图 5 已保存")

# ----- 图 6（选做）：ROE 对比 -----
try:
    fin = pd.read_csv("data/finance/finance_ratios.csv")
    if "indicator" in fin.columns:
        roe = fin[fin["indicator"] == "净资产收益率(ROE)"].copy()
    else:
        roe = pd.DataFrame()
    if len(roe) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        for stock in stocks:
            s = roe[roe["code"] == stock["code"]]
            if len(s) > 0:
                ax.plot(s["year"], s["value"], "o-",
                        color=industry_colors.get(stock["industry"], "gray"),
                        label=f"{stock['name']}({stock['industry']})",
                        linewidth=1.5, markersize=5)
        ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
        ax.set_xlabel("年份", fontsize=12)
        ax.set_ylabel("ROE (%)", fontsize=12)
        ax.set_title("图 6：各股票 ROE 趋势对比（按行业着色）",
                     fontsize=13, fontweight="bold")
        ax.legend(fontsize=8, ncol=2)
        plt.tight_layout()
        plt.savefig("output/fig6_roe_comparison.png", dpi=150, bbox_inches="tight")
        plt.close()
        print("图 6 已保存")
    else:
        print("图 6 跳过：ROE 数据为空")
except Exception as e:
    print(f"图 6 跳过: {e}")

# ----- 完成 -----
print(f"\n===== 全部完成 =====")
print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("输出文件清单：")
for f in sorted(os.listdir("output")):
    size = os.path.getsize(f"output/{f}") / 1024
    print(f"  output/{f}: {size:.1f} KB")
