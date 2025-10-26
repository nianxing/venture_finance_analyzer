# ZFarm Decision System

🌾 **农业创新融资决策分析系统**

一个用于分析股权稀释、DCF估值和风险模拟的决策支持工具。

## ✨ 功能特性

### 📊 股权稀释分析
- **母公司稀释**: 模拟多轮融资后的股权稀释情况
- **JV稀释分析**: 合资企业的多方股权变化模拟
- 详细的数据表格和可视化图表

### 💰 估值分析
- **DCF模型**: 现金流折现和终值计算
- **退出估值**: 完整的估值分析
- **投资回报率(ROI)**: 量化投资回报

### 🎲 风险模拟
- **蒙特卡洛模拟**: 10,000+次模拟
- **风险量化**: 均值、中位数、分位数分析
- **不确定性分析**: 现金流波动和退出估值分布

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

### 命令行模式
```bash
cd zfarm_decision_system
python main.py
```

报告将生成在 `reports/decision_summary.md`

### Web界面
```bash
cd zfarm_decision_system
python app.py
```

然后打开浏览器访问: **http://localhost:5000**

## 📦 项目结构

```
zfarm_decision_system/
├── core/                      # 核心业务逻辑
│   ├── cap_table_main.py     # 母公司稀释模拟
│   ├── cap_table_jointventure.py  # JV稀释模拟
│   ├── dcf_model.py           # DCF估值计算
│   ├── exit_analysis.py       # 退出分析
│   └── montecarlo_risk.py    # 蒙特卡洛模拟
├── data/                      # 数据文件
│   ├── assumptions.yaml       # 配置文件
│   └── input_financing.xlsx   # 融资输入数据
├── templates/                 # Web界面模板
│   └── index.html             # 主页面
├── static/                    # 静态资源
│   └── main.js                # 前端逻辑
├── reports/                   # 输出报告
│   └── decision_summary.md    # 决策摘要
├── app.py                     # Flask应用
├── main.py                    # 命令行入口
└── requirements.txt           # 依赖列表
```

## 📚 使用文档

- [Web界面使用指南](zfarm_decision_system/WEB_USAGE.md) - Web界面详细说明
- [Web可视化总结](WEB_VISUALIZATION_SUMMARY.md) - Web功能总结
- [改进记录](IMPROVEMENTS.md) - 代码改进历史

## 🎯 使用示例

### 母公司稀释分析
```python
from core.cap_table_main import simulate_equity_dilution

pre_money = 2000.0
rounds = [
    {'round': 'Seed', 'amount': 500.0},
    {'round': 'A', 'amount': 1500.0}
]
result = simulate_equity_dilution(pre_money, rounds)
print(result)
```

### 退出估值分析
```python
from core.exit_analysis import analyze_exit

cash_flows = [200.0, 400.0, 800.0, 1200.0, 1500.0]
result = analyze_exit(
    cash_flows, 
    discount_rate=0.12,
    growth_rate=0.03,
    investor_share=0.2,
    invested_amount=1500.0
)
print(result)
```

## 🛠️ 技术栈

- **后端**: Python, Flask, pandas, numpy
- **前端**: HTML5, CSS3, JavaScript, Chart.js
- **分析**: DCF模型, 蒙特卡洛模拟

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**Enjoy analyzing! 🚀**

