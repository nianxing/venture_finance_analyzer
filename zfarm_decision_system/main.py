"""
ZFarm Decision System - Main Entry Point
Demo runner for zfarm_decision_system
"""
from core.cap_table_main import simulate_equity_dilution
from core.cap_table_jointventure import simulate_jv_equity
from core.exit_analysis import analyze_exit
from core.montecarlo_risk import monte_carlo_exit_analysis
import pandas as pd
import yaml
from datetime import datetime
import os


def load_assumptions(config_path='data/assumptions.yaml'):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file {config_path} not found, using defaults")
        return {
            'currency': 'CNY',
            'unit': 'thousand',
            'discount_rate': 0.12,
            'growth_rate': 0.03,
            'montecarlo_trials': 10000
        }


def run_demo():
    """运行演示分析"""
    print("=== ZFarm Decision System Demo ===\n")
    
    # 加载配置
    config = load_assumptions()
    print(f"Loaded configuration: {config.get('currency', 'CNY')} currency, "
          f"discount_rate={config.get('discount_rate', 0.12)}, "
          f"growth_rate={config.get('growth_rate', 0.03)}\n")
    
    # 1. 母公司稀释分析
    print("1. Analyzing parent company dilution...")
    parent_pre = 2000.0
    rounds = [{'round': 'Seed', 'amount': 500.0}, {'round': 'A', 'amount': 1500.0}]
    parent = simulate_equity_dilution(parent_pre, rounds)
    print("✓ Parent dilution analysis completed")
    
    # 2. JV稀释分析
    print("\n2. Analyzing JV equity dilution...")
    initial_inv = {'ag_inno': 100.0, 'partner': 150.0, 'grant': 0.0}
    rounds_jv = [
        {'round': 'A', 'amount': 500.0},
        {'round': 'B', 'amount': 1000.0},
        {'round': 'C', 'amount': 2000.0}
    ]
    jv = simulate_jv_equity(initial_inv, rounds_jv)
    print("✓ JV dilution analysis completed")
    
    # 3. 退出分析
    print("\n3. Performing exit analysis...")
    cash_flows = [200.0, 400.0, 800.0, 1200.0, 1500.0]
    res = analyze_exit(cash_flows, 0.12, 0.03, 0.2, 1500.0)
    print("✓ Exit analysis completed")
    
    # 4. 蒙特卡洛风险分析
    print("\n4. Running Monte Carlo simulation...")
    mc_results = monte_carlo_exit_analysis(
        cash_flows, 
        0.12, 0.03, 0.2, 1500.0,
        trials=config.get('montecarlo_trials', 10000),
        cf_volatility=0.2
    )
    print("✓ Monte Carlo simulation completed")
    
    # 5. 生成报告
    print("\n5. Generating report...")
    
    # 确保报告目录存在
    os.makedirs('reports', exist_ok=True)
    
    with open('reports/decision_summary.md', 'w', encoding='utf-8') as f:
        f.write(f'# ZFarm Decision System - Analysis Report\n\n')
        f.write(f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write('---\n\n')
        
        # 母公司稀释
        f.write('## 1. 母公司股权稀释分析\n\n')
        f.write('### 稀释模拟结果\n\n')
        f.write(parent.to_markdown(index=False))
        f.write('\n\n')
        final_dilution = parent['founders_pct'].iloc[-1] if not parent.empty else 1.0
        f.write(f'**最终创始人持股**: {final_dilution*100:.2f}%\n\n')
        f.write('---\n\n')
        
        # JV稀释
        f.write('## 2. 合资企业股权稀释分析\n\n')
        f.write('### JV稀释模拟结果\n\n')
        f.write(jv.to_markdown(index=False))
        f.write('\n\n')
        if not jv.empty:
            final_row = jv.iloc[-1]
            f.write(f'**最终持股比例**:\n')
            f.write(f'- AgInno: {final_row["ag_inno_pct"]*100:.2f}%\n')
            f.write(f'- Partner: {final_row["partner_pct"]*100:.2f}%\n')
            f.write(f'- Grant: {final_row["grant_pct"]*100:.2f}%\n')
            f.write(f'- External: {final_row["external_pct"]*100:.2f}%\n')
        f.write('\n---\n\n')
        
        # 退出分析
        f.write('## 3. 退出估值分析\n\n')
        f.write('### DCF估值结果\n\n')
        f.write(f'- **现金流现值**: {config.get("currency", "CNY")} {res["pv_cashflows"]:,.0f}万\n')
        f.write(f'- **终值**: {config.get("currency", "CNY")} {res["terminal_value"]:,.0f}万\n')
        f.write(f'- **退出估值**: {config.get("currency", "CNY")} {res["exit_valuation"]:,.0f}万\n')
        f.write(f'- **投资回报率(ROI)**: {res["investor_roi"]*100:.2f}%\n\n')
        f.write('---\n\n')
        
        # 蒙特卡洛风险分析
        if mc_results:
            f.write('## 4. 蒙特卡洛风险分析\n\n')
            f.write(f'**模拟次数**: {mc_results["trials_count"]}\n\n')
            f.write('### 退出估值风险分析\n\n')
            f.write(f'- **均值**: {config.get("currency", "CNY")} {mc_results["mean_exit_value"]:,.0f}万\n')
            f.write(f'- **中位数**: {config.get("currency", "CNY")} {mc_results["median_exit_value"]:,.0f}万\n')
            f.write(f'- **标准差**: {config.get("currency", "CNY")} {mc_results["std_exit_value"]:,.0f}万\n')
            f.write(f'- **10%分位数**: {config.get("currency", "CNY")} {mc_results["p10_exit_value"]:,.0f}万\n')
            f.write(f'- **90%分位数**: {config.get("currency", "CNY")} {mc_results["p90_exit_value"]:,.0f}万\n\n')
            f.write('### 投资回报率风险分析\n\n')
            f.write(f'- **均值ROI**: {mc_results["mean_roi"]*100:.2f}%\n')
            f.write(f'- **中位数ROI**: {mc_results["median_roi"]*100:.2f}%\n')
            f.write(f'- **10%分位数ROI**: {mc_results["p10_roi"]*100:.2f}%\n')
            f.write(f'- **90%分位数ROI**: {mc_results["p90_roi"]*100:.2f}%\n\n')
        else:
            f.write('## 4. 蒙特卡洛风险分析\n\n')
            f.write('⚠️ Monte Carlo simulation did not produce valid results.\n\n')
        
        f.write('---\n\n')
        f.write('## 总结\n\n')
        f.write('以上分析展示了不同融资场景下的股权稀释情况和投资回报预测。\n')
    
    print('✓ Report generated: reports/decision_summary.md')
    print("\n=== Analysis Complete ===\n")


if __name__ == '__main__':
    run_demo()
