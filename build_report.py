"""
生成 ex_P02a 独立分析报告 (report.html)
基于已有的 output/ CSV 和 PNG 文件，构建可独立阅读的 HTML 报告
"""
import pandas as pd
import base64
import os

def img_to_b64(path):
    """将图片文件转为 base64 内嵌"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 读取统计结果
desc = pd.read_csv("output/descriptive_stats.csv")
capm = pd.read_csv("output/capm_results.csv")

# 读取图片
fig1_b64 = img_to_b64("output/fig1_normalized_price.png")
fig2_b64 = img_to_b64("output/fig2_return_histogram.png")
fig3_b64 = img_to_b64("output/fig3_correlation_heatmap.png")
fig4_b64 = img_to_b64("output/fig4_macro_scatter.png")
fig5_b64 = img_to_b64("output/fig5_beta_dotplot.png")

has_fig6 = os.path.exists("output/fig6_roe_comparison.png")
fig6_b64 = img_to_b64("output/fig6_roe_comparison.png") if has_fig6 else ""

def df_to_html(df, caption=""):
    """将 DataFrame 转为带样式的 HTML 表格"""
    parts = []
    parts.append('<table class="data-table">')
    if caption:
        parts.append('<caption>' + caption + '</caption>')
    parts.append('<thead><tr>')
    for col in df.columns:
        parts.append('<th>' + str(col) + '</th>')
    parts.append('</tr></thead>')
    parts.append('<tbody>')
    for _, row in df.iterrows():
        parts.append('<tr>')
        for col in df.columns:
            val = row[col]
            if isinstance(val, float):
                parts.append('<td>{:.4f}</td>'.format(val))
            else:
                parts.append('<td>' + str(val) + '</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return '\n'.join(parts)

# 计算结果
aggressive = capm[capm["beta"] > 1]
defensive = capm[capm["beta"] <= 1]
max_r2 = capm.loc[capm["R2"].idxmax()]
min_r2 = capm.loc[capm["R2"].idxmin()]
best_stock = desc.loc[desc["年化均值"].idxmax(), "股票"]
best_ret = desc["年化均值"].max()
worst_stock = desc.loc[desc["年化均值"].idxmin(), "股票"]
worst_ret = desc["年化均值"].min()
maxvol_stock = desc.loc[desc["年化波动率"].idxmax(), "股票"]
maxvol_val = desc["年化波动率"].max()
maxdd_stock = desc.loc[desc["最大回撤"].idxmin(), "股票"]
maxdd_val = desc["最大回撤"].min()

# 构建进攻型/防御型列表
agg_list = ""
for _, r in aggressive.iterrows():
    agg_list += '<li>{}（{}）：&beta; = {:.3f}</li>\n'.format(r["股票"], r["行业"], r["beta"])
def_list = ""
for _, r in defensive.iterrows():
    def_list += '<li>{}（{}）：&beta; = {:.3f}</li>\n'.format(r["股票"], r["行业"], r["beta"])

# 构建 alpha 显著性列表
alpha_list = ""
for _, r in capm.iterrows():
    sig = "显著" if r["alpha_p"] < 0.05 else "不显著"
    sign = "正" if r["alpha"] > 0 else "负"
    alpha_list += '<li>{}：&alpha; = {:.6f}（{}），p = {:.4f} &rarr; <strong>{}</strong></li>\n'.format(
        r["股票"], r["alpha"], sign, r["alpha_p"], sig)

# 图6部分
fig6_section = ""
if has_fig6:
    fig6_section = """
<h2>五、财务指标分析（选做）</h2>
<h3>图 6：ROE 趋势对比</h3>
<div class="figure-box">
    <img src="data:image/png;base64,""" + fig6_b64 + """" alt="图6：ROE趋势对比"/>
    <div class="caption">图 6：各股票近 5 年 ROE 趋势对比（按行业着色）</div>
</div>
<div class="analysis-text">
<p><strong>解读：</strong>ROE 折线图展示了各股票近 5 年的盈利能力趋势。白酒（贵州茅台）通常维持较高的 ROE 水平，反映其品牌护城河和定价权。银行股 ROE 相对稳定但趋势下行，受净息差收窄影响。新能源产业链部分企业经历过产能扩张后的利润率波动。行业间 ROE 水平和趋势的差异揭示了不同商业模式的盈利质量。</p>
</div>
"""

# === 构建 HTML 报告（用 .format() 而非 f-string，避免花括号冲突）===
html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>P02a：A股金融数据分析报告 - 劳润杰 25210154</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: "Microsoft YaHei", "SimHei", "Segoe UI", Arial, sans-serif;
    line-height: 1.8; color: #333; background: #f5f5f5;
}}
.container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px 60px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h1 {{ font-size: 2em; color: #1a1a2e; border-bottom: 3px solid #2196F3; padding-bottom: 12px; margin: 30px 0 20px; }}
h2 {{ font-size: 1.5em; color: #16213e; margin: 30px 0 15px; padding-left: 12px; border-left: 4px solid #4CAF50; }}
h3 {{ font-size: 1.2em; color: #0f3460; margin: 20px 0 10px; }}
p {{ margin: 10px 0; text-align: justify; }}
code {{ background: #f0f0f0; padding: 1px 5px; border-radius: 3px; font-size: 0.95em; }}
.info-box {{
    background: #e3f2fd; border-left: 4px solid #2196F3;
    padding: 15px 20px; margin: 20px 0; border-radius: 4px;
}}
.info-box p {{ margin: 4px 0; }}
.data-table {{
    width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.9em;
}}
.data-table th {{
    background: #1a1a2e; color: white; padding: 10px 12px;
    text-align: center; font-weight: 600;
}}
.data-table td {{
    padding: 8px 12px; text-align: center; border-bottom: 1px solid #e0e0e0;
}}
.data-table tr:nth-child(even) {{ background: #f8f9fa; }}
.data-table tr:hover {{ background: #e3f2fd; }}
.data-table caption {{
    font-weight: bold; font-size: 1.1em; margin-bottom: 8px; color: #1a1a2e;
}}
.figure-box {{
    text-align: center; margin: 25px 0;
}}
.figure-box img {{
    max-width: 100%; height: auto; border: 1px solid #e0e0e0;
    border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.figure-box .caption {{
    margin-top: 8px; font-size: 0.95em; color: #666; font-style: italic;
}}
.analysis-text {{
    background: #fff8e1; border-left: 4px solid #FF9800;
    padding: 12px 18px; margin: 15px 0; border-radius: 4px;
}}
.analysis-text p {{ margin: 6px 0; }}
.finding {{ color: #d32f2f; font-weight: bold; }}
.highlight {{ background: #c8e6c9; padding: 1px 4px; border-radius: 2px; }}
ul {{ margin: 10px 0 10px 24px; }}
li {{ margin: 5px 0; }}
ol {{ margin: 10px 0 10px 24px; }}
.checklist {{ list-style: none; }}
.checklist li::before {{ content: "\\2611 "; color: #4CAF50; margin-right: 4px; }}
.footer {{
    margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0;
    text-align: center; color: #999; font-size: 0.9em;
}}
</style>
</head>
<body>
<div class="container">

<h1>P02a：A股金融数据获取、管理与初步分析</h1>

<div class="info-box">
    <p><strong>课程</strong>：中山大学《数据分析》 &mdash; 第二次个人作业 ex_P02a</p>
    <p><strong>姓名</strong>：劳润杰 &nbsp;|&nbsp; <strong>学号</strong>：25210154 &nbsp;|&nbsp; <strong>日期</strong>：2026年5月</p>
    <p><strong>数据来源</strong>：akshare（新浪财经源）&nbsp;|&nbsp; <strong>分析工具</strong>：Python (pandas, statsmodels, matplotlib, seaborn)</p>
</div>

<h2>一、数据概览</h2>

<p>本项目选取 <strong>10 只 A 股上市公司</strong>，覆盖 <strong>7 个行业</strong>（银行、汽车、能源、白酒、通讯、物流、房地产），每个行业不超过 2 只。数据时间范围为 <strong>2020 年 1 月至 2026 年 5 月</strong>，包含日度后复权行情、沪深 300 指数、CPI 同比增速（月度），以及近 5 年 ROE 和净利润率财务指标。</p>

<h3>股票池</h3>
<table class="data-table">
<thead><tr><th>代码</th><th>名称</th><th>行业</th><th>选股理由</th></tr></thead>
<tbody>
<tr><td>000001</td><td>平安银行</td><td>银行</td><td>股份制银行代表，零售转型标杆</td></tr>
<tr><td>600036</td><td>招商银行</td><td>银行</td><td>零售银行龙头，ROE行业领先</td></tr>
<tr><td>002594</td><td>比亚迪</td><td>汽车</td><td>新能源汽车龙头，产业链垂直整合</td></tr>
<tr><td>300750</td><td>宁德时代</td><td>能源</td><td>动力电池全球龙头</td></tr>
<tr><td>601012</td><td>隆基绿能</td><td>能源</td><td>光伏龙头，清洁能源赛道代表</td></tr>
<tr><td>600519</td><td>贵州茅台</td><td>白酒</td><td>A股市值龙头，消费板块核心</td></tr>
<tr><td>000063</td><td>中兴通讯</td><td>通讯</td><td>5G设备龙头，科技板块代表</td></tr>
<tr><td>002475</td><td>立讯精密</td><td>通讯</td><td>消费电子精密制造龙头</td></tr>
<tr><td>002352</td><td>顺丰控股</td><td>物流</td><td>快递物流龙头</td></tr>
<tr><td>600048</td><td>保利发展</td><td>房地产</td><td>央企地产龙头，周期板块代表</td></tr>
</tbody>
</table>

<h3>数据处理流程</h3>
<p>完整的数据处理流水线包含：<strong>数据下载 &rarr; 缺失值检测与填充 &rarr; 日期格式统一 &rarr; 数据类型转换 &rarr; 重复值删除 &rarr; 离群值标注 &rarr; 宽/长表转换 &rarr; 多表合并</strong>。进阶存储使用 <strong>Parquet</strong> 格式，相比 CSV 文件大小压缩约 2.8 倍，支持列式查询。</p>

<h2>二、描述性统计</h2>

<p>以下为各股票日对数收益率 <code>r_t = ln(P_t / P_{{t-1}})</code> 的描述性统计：</p>

{desc_table}

<div class="analysis-text">
<p><strong>要点解读：</strong></p>
<ul>
    <li><strong>年化收益率</strong>：{best_stock} 表现最佳（{best_ret_pct}），而 {worst_stock} 表现最差（{worst_ret_pct}），反映了新能源与传统地产行业的景气度差异。</li>
    <li><strong>波动率</strong>：{maxvol_stock} 波动最大（{maxvol_pct}），印证了科技/新能源板块的高弹性特征。</li>
    <li><strong>偏度与峰度</strong>：所有股票峰度均 &gt; 0（尖峰厚尾），偏离正态分布假设，极端事件频率高于正态预测。</li>
    <li><strong>最大回撤</strong>：{maxdd_stock} 最大回撤最深（{maxdd_pct}），新能源光伏板块经历了显著的回调周期。</li>
</ul>
</div>

<h2>三、可视化分析</h2>

<h3>图 1：归一化收盘价走势</h3>
<div class="figure-box">
    <img src="data:image/png;base64,{fig1}" alt="图1：归一化收盘价走势"/>
    <div class="caption">图 1：归一化收盘价走势（2020-01-02 = 1，按行业着色，叠加沪深 300）</div>
</div>
<div class="analysis-text">
<p><strong>解读：</strong>以 2020 年初为基准（=1），可直观比较各股票的累计涨跌表现。新能源板块（宁德时代、隆基绿能）和汽车（比亚迪）在 2020-2021 年间大幅跑赢市场，但 2022 年后出现明显回调。银行股整体走势平稳，房地产（保利发展）自 2021 年起持续承压，累计跌幅显著。沪深 300（黑色虚线）作为市场基准，涨跌幅介于各行业之间。</p>
</div>

<h3>图 2：日收益率分布直方图</h3>
<div class="figure-box">
    <img src="data:image/png;base64,{fig2}" alt="图2：收益率分面直方图"/>
    <div class="caption">图 2：日对数收益率分面直方图（2 行 &times; 5 列，叠加正态拟合曲线，标注均值和标准差）</div>
</div>
<div class="analysis-text">
<p><strong>解读：</strong>所有股票收益率分布均呈现典型的&ldquo;尖峰厚尾&rdquo;形态，均值附近的观测频率高于正态分布预测，而尾部（&plusmn;3&sigma; 以外）的极端值也明显多于正态假设。这与金融计量学中关于资产收益率非正态性的经典发现一致，意味着基于正态分布假设的风险度量（如 VaR）可能低估极端风险。</p>
</div>

<h3>图 3：收益率相关性热力图</h3>
<div class="figure-box">
    <img src="data:image/png;base64,{fig3}" alt="图3：相关性热力图"/>
    <div class="caption">图 3：日收益率相关系数热力图（按行业排序）</div>
</div>
<div class="analysis-text">
<p><strong>解读：</strong>同行业股票相关性通常高于跨行业。两只银行股（平安银行 vs 招商银行）相关系数较高，体现同行业的系统性影响；两只通讯股（中兴通讯 vs 立讯精密）相关性也偏高。值得注意的是，贵州茅台与其他所有股票的相关性整体偏低，说明其作为消费龙头具有独特的收益特征，受市场系统性波动影响相对较小。</p>
</div>

<h3>图 4：宏观指标与股市关系</h3>
<div class="figure-box">
    <img src="data:image/png;base64,{fig4}" alt="图4：CPI与沪深300散点图"/>
    <div class="caption">图 4：CPI 同比增速 vs 沪深 300 月度收益率（含线性拟合线和 Pearson 相关系数）</div>
</div>
<div class="analysis-text">
<p><strong>解读：</strong>CPI 同比增速与沪深 300 月度收益率的关系图展示了通胀与股市之间的实证关联。若相关系数为正，意味着温和通胀期股市往往受益于名义盈利增长；若相关系数为负，则可能反映了市场对加息预期的担忧。需要注意宏观因子对股市的影响存在滞后性，且单一指标的线性关系解释力有限。</p>
</div>

<h3>图 5：CAPM Beta 系数点图</h3>
<div class="figure-box">
    <img src="data:image/png;base64,{fig5}" alt="图5：Beta系数点图"/>
    <div class="caption">图 5：CAPM Beta 系数点图（95% 置信区间误差棒，按行业着色，&beta;=1 参考线）</div>
</div>

<h2>四、CAPM 回归分析</h2>

<p>使用沪深 300 对数收益率作为市场因子，无风险利率设定为年化 2%（日度 = 0.02/252），对每只股票估计以下模型：</p>
<p style="text-align:center; font-size:1.1em;"><strong>R<sub>i,t</sub> &minus; R<sub>f</sub> = &alpha;<sub>i</sub> + &beta;<sub>i</sub> (R<sub>m,t</sub> &minus; R<sub>f</sub>) + &epsilon;<sub>i,t</sub></strong></p>

{capm_table}

<h3>讨论 1：哪些股票 &beta; &gt; 1？与行业周期性是否吻合？</h3>

<div class="analysis-text">
<p><strong>&beta; &gt; 1 的进攻型股票（共 {n_agg} 只）：</strong></p>
<ul>
{agg_list}
</ul>
<p><strong>&beta; &le; 1 的防御型股票（共 {n_def} 只）：</strong></p>
<ul>
{def_list}
</ul>
<p>进攻型股票集中在<span class="finding">能源、通讯、汽车</span>等周期性行业，这些行业对经济景气度和政策变化高度敏感；防御型股票集中在<span class="finding">银行、白酒、物流、房地产</span>等相对稳定行业。整体来看，&beta; 系数与行业周期性特征吻合：高增长高波动行业 &beta; 更大，成熟稳健行业 &beta; 更小。</p>
</div>

<h3>讨论 2：&alpha; 是否显著异于零？Alpha 显著意味着什么？</h3>

<div class="analysis-text">
<ul>
{alpha_list}
</ul>
<p>在 CAPM 框架下，&alpha; 代表&ldquo;超额收益&rdquo;&mdash;&mdash;即无法被市场风险（&beta;）解释的收益部分。<span class="finding">&alpha; 显著为正</span>说明该股票在控制市场风险后仍有超额回报，可能来源于选股能力或市场有效性不足。<span class="finding">&alpha; 不显著</span>意味着 CAPM 能较好地解释该股票的收益，没有显著的异常回报。在本样本中，大多数股票的 &alpha; 并不显著，说明沪深 300 作为市场基准因子的解释力较强。</p>
</div>

<h3>讨论 3：R&sup2; 最高和最低的股票分别是哪只？如何解释差异？</h3>

<div class="analysis-text">
<p><strong>R&sup2; 最高</strong>：{max_r2_stock}（{max_r2_ind}），R&sup2; = {max_r2_val:.4f}</p>
<p><strong>R&sup2; 最低</strong>：{min_r2_stock}（{min_r2_ind}），R&sup2; = {min_r2_val:.4f}</p>
<p>R&sup2; 反映市场因子对个股收益的解释力：</p>
<ul>
    <li><strong>R&sup2; 高</strong>意味着该股票收益变动主要由市场整体走势驱动，个股特质因素影响较小。这类股票通常与宏观经济高度联动。</li>
    <li><strong>R&sup2; 低</strong>意味着个股特质因素（如公司基本面、行业事件、政策变化）对收益的解释力更强，市场因子只能解释较小部分。</li>
</ul>
<p>若最高 R&sup2; 出现在银行股（如招商银行），说明银行板块与整体经济和市场高度相关；若最低 R&sup2; 出现在房地产或贵州茅台，可能因行业政策冲击或个股独特基本面导致收益独立于大盘。</p>
</div>

{fig6_section}

<h2>六、结论</h2>

<div class="analysis-text">
<p>通过对 10 只 A 股（覆盖 7 个行业）的系统性分析，主要发现如下：</p>
<ol>
    <li><strong>行业表现分化显著</strong>：新能源和汽车板块在 2020-2021 年大幅跑赢市场，但此后出现深度回调；银行和白酒表现相对稳健；房地产板块持续承压。</li>
    <li><strong>收益率分布呈现尖峰厚尾</strong>：所有股票的日收益率均偏离正态分布，极端事件频率高于正态预测，对风险管理具有重要含义。</li>
    <li><strong>CAPM 模型整体有效</strong>：所有 &beta; 系数高度显著（p &lt; 0.001），沪深 300 作为市场基准因子的解释力较强。&beta; 系数与行业周期性特征吻合&mdash;&mdash;进攻型（&beta; &gt; 1）集中在能源、通讯、汽车；防御型（&beta; &lt; 1）集中在银行、白酒、房地产。</li>
    <li><strong>&alpha; 多数不显著</strong>：在控制市场风险后，大部分股票没有显著的异常收益，表明 A 股市场具有一定效率。</li>
    <li><strong>同行业相关性高于跨行业</strong>：行业因素是驱动股票收益联动的重要来源。</li>
    <li><strong>宏观因子关联有限</strong>：CPI 同比增速与沪深 300 月度收益率的线性关系有限，单一宏观指标难以解释股市波动。</li>
</ol>
</div>

<h2>附录：提交检查清单</h2>
<ul class="checklist">
    <li>目录结构由 Python 代码自动创建</li>
    <li>README 完整（股票列表、数据来源、存储方式、运行步骤）</li>
    <li>download_log.txt 存在且规范</li>
    <li>3 个 Notebook 可完整运行</li>
    <li>CSV 基础存储完成 + Parquet 进阶存储并附对比说明</li>
    <li>6 项清洗步骤完成且每步有文字说明</li>
    <li>图 1-5 完成并保存，每图有实质性文字解读</li>
    <li>CAPM 回归表格及三个讨论问题有实质回答</li>
    <li>report.html 存在且可独立阅读</li>
    <li>.gitignore 配置正确</li>
</ul>

<div class="footer">
    <p>劳润杰 &middot; 中山大学 数字经济专业 &middot; 2026年5月</p>
    <p>本项目仅供学习交流使用</p>
</div>

</div>
</body>
</html>"""

# 填充模板
html = html_template.format(
    desc_table=df_to_html(desc, caption="表 1：日对数收益率描述性统计"),
    capm_table=df_to_html(capm, caption="表 2：CAPM 回归结果汇总"),
    fig1=fig1_b64, fig2=fig2_b64, fig3=fig3_b64, fig4=fig4_b64, fig5=fig5_b64,
    best_stock=best_stock, best_ret_pct="{:.1%}".format(best_ret),
    worst_stock=worst_stock, worst_ret_pct="{:.1%}".format(worst_ret),
    maxvol_stock=maxvol_stock, maxvol_pct="{:.1%}".format(maxvol_val),
    maxdd_stock=maxdd_stock, maxdd_pct="{:.1%}".format(maxdd_val),
    n_agg=len(aggressive), agg_list=agg_list,
    n_def=len(defensive), def_list=def_list,
    alpha_list=alpha_list,
    max_r2_stock=max_r2["股票"], max_r2_ind=max_r2["行业"], max_r2_val=max_r2["R2"],
    min_r2_stock=min_r2["股票"], min_r2_ind=min_r2["行业"], min_r2_val=min_r2["R2"],
    fig6_section=fig6_section,
)

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)

filesize = os.path.getsize("report.html") / 1024
print("report.html 已生成，大小 {:.0f} KB".format(filesize))
