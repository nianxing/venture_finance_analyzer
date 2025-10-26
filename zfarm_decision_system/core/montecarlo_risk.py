"""montecarlo_risk.py - Monte Carlo helpers"""
import numpy as np
import pandas as pd

def simulate_delay(trials, optimistic, likely, pessimistic):
    """
    模拟项目延迟（三角分布）
    
    Args:
        trials: 模拟次数
        optimistic: 乐观估计
        likely: 最可能值
        pessimistic: 悲观估计
    
    Returns:
        模拟结果数组
    """
    if not (optimistic <= likely <= pessimistic):
        raise ValueError("Must have optimistic <= likely <= pessimistic")
    
    return np.random.triangular(optimistic, likely, pessimistic, size=trials)


def simulate_revenue_scenarios(trials, base_revenue, volatility):
    """
    模拟收入场景（正态分布）
    
    Args:
        trials: 模拟次数
        base_revenue: 基准收入
        volatility: 波动率（标准差/基准收入）
    
    Returns:
        模拟结果数组
    """
    if base_revenue <= 0:
        raise ValueError("base_revenue must be positive")
    
    if volatility < 0:
        raise ValueError("volatility cannot be negative")
    
    return np.random.normal(loc=base_revenue, scale=base_revenue * volatility, size=trials)


def monte_carlo_exit_analysis(cash_flows, discount_rate, growth_rate, investor_share, 
                              invested_amount, trials=10000, cf_volatility=0.2):
    """
    蒙特卡洛退出分析
    
    Args:
        cash_flows: 基准现金流列表
        discount_rate: 折现率
        growth_rate: 永续增长率
        investor_share: 投资者持股比例
        invested_amount: 投资金额
        trials: 模拟次数
        cf_volatility: 现金流波动率
    
    Returns:
        包含统计结果的字典
    """
    from .dcf_model import calculate_dcf, terminal_value, exit_valuation
    
    results = []
    
    for _ in range(trials):
        # 模拟现金流波动
        simulated_cf = [
            cf * (1 + np.random.normal(0, cf_volatility)) for cf in cash_flows
        ]
        
        try:
            pv = calculate_dcf(simulated_cf, discount_rate)
            tv = terminal_value(simulated_cf[-1], growth_rate, discount_rate)
            
            if tv is not None:
                ev = exit_valuation(pv, tv)
                if invested_amount > 0:
                    proceeds = ev * investor_share
                    roi = (proceeds - invested_amount) / invested_amount
                    results.append({
                        'exit_value': ev,
                        'roi': roi
                    })
        except:
            continue
    
    if not results:
        return None
    
    df = pd.DataFrame(results)
    
    return {
        'mean_exit_value': float(df['exit_value'].mean()),
        'median_exit_value': float(df['exit_value'].median()),
        'std_exit_value': float(df['exit_value'].std()),
        'p10_exit_value': float(df['exit_value'].quantile(0.1)),
        'p90_exit_value': float(df['exit_value'].quantile(0.9)),
        'mean_roi': float(df['roi'].mean()),
        'median_roi': float(df['roi'].median()),
        'p10_roi': float(df['roi'].quantile(0.1)),
        'p90_roi': float(df['roi'].quantile(0.9)),
        'trials_count': len(results)
    }
