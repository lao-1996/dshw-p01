# P02a：A股金融数据获取、管理与初步分析

> 中山大学《数据分析》课程 — 第二次个人作业 ex_P02a  
> **姓名**：劳润杰　**学号**：25210154　**日期**：2026年5月

---

## 一、项目简介

本项目实现了一套完整、可复现的 A 股金融数据处理流程：从 akshare 获取 10 只 A 股（覆盖 7 个行业）的日度行情、沪深 300 指数、CPI 与 M2 宏观指标、财务指标，经数据清洗与多表合并后，进行描述统计、可视化分析和 CAPM 回归。

---

## 二、数据来源

| 数据类别 | 来源工具 | 说明 |
|----------|----------|------|
| 个股日度行情 | akshare（新浪财经源） | 后复权，2020-01-01 至今 |
| 市场指数 | akshare | 沪深 300（000300）+ 中证 500（000905） |
| 宏观指标 | akshare | CPI 同比增速（必选）、M2 增速（自选） |
| 财务指标 | akshare | ROE、净利润率（近 5 年），长格式 |

**选择 M2 增速作为自选宏观指标的理由**：M2 反映货币供应总量，宽松货币环境通常推升资产价格，紧缩环境则相反，是影响 A 股流动性的核心指标之一。

---

## 三、股票池与选股理由

选取 10 只 A 股，覆盖 **7 个行业**（≥5），每个行业 ≤2 只：

| 代码 | 名称 | 行业 | 选股理由 |
|------|------|------|----------|
| 000001 | 平安银行 | 银行 | 股份制银行代表，零售转型标杆 |
| 600036 | 招商银行 | 银行 | 零售银行龙头，ROE 行业领先 |
| 002594 | 比亚迪 | 汽车 | 新能源汽车龙头，产业链垂直整合 |
| 300750 | 宁德时代 | 能源（新能源） | 动力电池全球龙头，行业标杆 |
| 601012 | 隆基绿能 | 能源（新能源） | 光伏龙头，代表清洁能源赛道 |
| 600519 | 贵州茅台 | 白酒 | A 股市值龙头，消费板块核心标的 |
| 000063 | 中兴通讯 | 通讯 | 5G 设备龙头，科技板块代表 |
| 002475 | 立讯精密 | 通讯 | 消费电子精密制造龙头 |
| 002352 | 顺丰控股 | 物流 | 快递物流龙头，现代服务业代表 |
| 600048 | 保利发展 | 房地产 | 央企地产龙头，周期板块代表 |

---

## 四、原始数据文件说明

| 文件名 | 主要内容 | 使用变量 | 格式 |
|--------|----------|----------|------|
| `stock_XXXXXX.csv` | 个股日度 OHLCV 行情 | date, open, high, low, close, volume | CSV |
| `index_000300.csv` | 沪深 300 日度行情 | date, close | CSV |
| `index_000905.csv` | 中证 500 日度行情 | date, close | CSV |
| `macro_cpi.csv` | CPI 月度数据 | 日期, 今值（CPI 同比） | CSV |
| `macro_m2.csv` | M2 月度数据 | 月份, m2（M2 同比增速） | CSV |
| `finance_ratios.csv` | 财务指标（长格式） | code, year, indicator, value | CSV |

---

## 五、项目结构

```
dshw-p01/
├── README.md               # 本文件
├── report.html             # 独立分析报告（nbconvert 导出）
├── requirements.txt        # Python 依赖
├── .gitignore              # Git 忽略规则
├── download_log.txt        # 下载日志
├── 01_download.ipynb       # 数据下载
├── 02_clean.ipynb          # 数据清洗与合并
├── 03_analysis.ipynb       # 描述统计、可视化、CAPM 回归
├── data/
│   ├── stock/              # 原始个股 CSV（10 只）
│   ├── index/              # 原始指数 CSV（2 个）
│   ├── macro/              # 原始宏观 CSV（2 个）
│   ├── finance/            # 财务指标 CSV（1 个）
│   ├── clean/              # 清洗后数据（CSV + Parquet）
│   └── combined/           # 合并后综合数据（CSV + Parquet）
└── output/                 # 图表 PNG + 结果 CSV
    ├── descriptive_stats.csv
    ├── capm_results.csv
    ├── fig1_normalized_price.png
    ├── fig2_return_histogram.png
    ├── fig3_correlation_heatmap.png
    ├── fig4_macro_scatter.png
    └── fig5_beta_dotplot.png
```

---

## 六、数据清洗说明

### 清洗步骤（6 项，详见 `02_clean.ipynb`）

| 步骤 | 方法 | 说明 |
|------|------|------|
| 缺失值检测 | 统计每列缺失数量/比例 | 缺失主要来自非交易日（周末/节假日），部分股票上市较晚导致早期缺失 |
| 缺失值处理 | 前向填充（ffill） | 对停牌/非交易日填充前一有效值；上市前缺失不做处理 |
| 日期格式 | 统一为 `datetime64`，设为索引 | 确保时间序列操作兼容 |
| 数据类型 | 价格/成交量转为 float64 | 若存在字符型需转换并记录 |
| 重复值处理 | 删除 date 重复行（保留最后） | 删除数量在日志中记录 |
| 离群值标注 | `is_extreme` 列标 True | 日对数收益率绝对值 > ln(1.20) 即 ±20% 以上，不删除，仅标注 |

### 宽表与长表转换（`02_clean.ipynb` 演示）

- **宽表**（行=日期，列=股票代码）：适合时间序列分析、计算收益率相关性矩阵、多股票走势对照
- **长表**（每行一条观测，date + code + close）：适合分组聚合（groupby）、多表合并（merge）、可视化（seaborn hue）
- 使用 `pd.pivot_table` 转宽表，`pd.melt` 回转长表

### 多表合并

| 合并步骤 | 合并方式 | 合并前 | 合并后 | 说明 |
|----------|----------|--------|--------|------|
| 个股 + 行业标签 | merge on code | 15,440 | 15,440 | 左连接，添加行业分类 |
| 个股 + 沪深 300 | merge on date | — | — | 左连接，添加市场对数收益率 |
| 日度 + CPI 月度 | merge on year_month | — | — | 月度 CPI 映射至每月所有交易日 |

---

## 七、存储方式

### 基础存储：CSV
- 所有原始数据、清洗后数据均以 CSV 格式保存
- **优点**：通用性强，任何工具可读；Git 可追踪差异；适合小规模数据
- **局限性**：无列类型信息，读写速度慢于二进制格式，不支持列式查询

### 进阶存储：Parquet（已完成）
- 额外保存 `data/combined/combined_data.parquet`
- **对比测试结果**：
  - 文件大小：CSV 2,330 KB → Parquet 843 KB（压缩比 **2.76x**）
  - 列式读取：只需读取 `close` 和 `log_return` 两列时，Parquet 可避免加载全部数据
- **结论**：当前数据规模（~1.5 万行）下 CSV 已足够高效；扩展至全 A 股日度数据（百万行级）时 Parquet 优势显著，建议使用

---

## 八、分析内容概览

### 描述性统计
- 各股票日对数收益率的年化均值、年化波动率、偏度、峰度、最大回撤

### 可视化
| 图号 | 内容 | 文件 |
|------|------|------|
| 图 1 | 归一化收盘价走势（2020-01-02=1）+ 沪深 300 | `fig1_normalized_price.png` |
| 图 2 | 日收益率分面直方图（2×5），叠加正态曲线 | `fig2_return_histogram.png` |
| 图 3 | 收益率相关系数热力图（按行业排序） | `fig3_correlation_heatmap.png` |
| 图 4 | CPI 同比 vs 沪深 300 月度收益率散点图 | `fig4_macro_scatter.png` |
| 图 5 | CAPM Beta 系数点图（95% CI，按行业着色） | `fig5_beta_dotplot.png` |
| 图 6（选做） | ROE 折线图（按行业分组） | `fig6_roe_comparison.png`（如有） |

### CAPM 回归
- 使用沪深 300 对数收益率作为市场因子，无风险利率年化 2%（日度 0.02/252）
- 估计模型：$r_{i,t} - r_f = \alpha_i + \beta_i (r_{m,t} - r_f) + \varepsilon_{i,t}$
- 讨论三个核心问题：β>1 的行业分布、α 显著性含义、R² 差异解释

---

## 九、GitHub 仓库

- **仓库地址**：https://github.com/lao-1996/dshw-p01
- **仓库名**：`dshw-p01`

---

## 十、如何运行

### 1. 环境准备
```bash
# 克隆仓库（如从 GitHub）
git clone <仓库地址>
cd dshw-p01

# 安装依赖
pip install -r requirements.txt
```

### 2. 按顺序运行 Notebook
1. `01_download.ipynb` → 下载原始数据到 `data/` 子目录
2. `02_clean.ipynb` → 清洗、合并、格式转换、存储
3. `03_analysis.ipynb` → 描述统计、可视化、CAPM 回归

### 3. 查看结果
- 分析报告：打开 `report.html`
- 图表：`output/` 目录下所有 PNG 文件
- 数据表：`output/` 目录下所有 CSV 文件

### 4. 他人如何重建数据
本项目原始数据文件未上传 GitHub（已通过 `.gitignore` 排除）。他人获取数据的方式：
1. 安装依赖后运行 `01_download.ipynb`，自动从 akshare 下载全部数据
2. 所有原始 CSV 将生成至 `data/stock/`、`data/index/`、`data/macro/`、`data/finance/`
3. 随后运行 `02_clean.ipynb` 和 `03_analysis.ipynb` 即可复现全部分析

---

## 十一、提交检查清单

- [x] 目录结构由 Python 代码创建
- [x] README 完整（股票列表、数据来源、存储方式、运行步骤）
- [x] `download_log.txt` 存在
- [x] 3 个 Notebook 可完整运行
- [x] CSV 基础存储完成 + Parquet 进阶存储对比说明
- [x] 6 项清洗步骤完成且每步有文字
- [x] 图 1-5 完成并保存，每图有解读
- [x] CAPM 回归表格及三个讨论问题回答
- [x] `report.html` 存在且可独立阅读
- [x] GitHub 仓库同步：https://github.com/lao-1996/dshw-p01
- [x] `.gitignore` 配置正确
- [ ] GitHub Pages（加分项，可选）

---

## 作者

劳润杰　中山大学 数字经济专业　2026 年 5 月

---

*本项目仅供学习交流使用。*
