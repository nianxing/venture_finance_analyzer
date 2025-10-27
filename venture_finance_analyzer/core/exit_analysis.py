"""exit_analysis.py - simple exit helper that uses dcf_model"""
from .dcf_model import calculate_dcf, terminal_value, exit_valuation, exit_return_on_investment

def analyze_exit(cash_flows, discount_rate, growth_rate, investor_share, invested_amount):
    """
    完整的退出分析
    
    Args:
        cash_flows: 现金流列表
        discount_rate: 折现率
        growth_rate: 永续增长率
        investor_share: 投资者持股比例
        invested_amount: 投资金额
    
    Returns:
        包含所有分析结果的字典
    """
    # 参数验证
    if not cash_flows:
        raise ValueError("cash_flows cannot be empty")
    
    if not (0 <= investor_share <= 1):
        raise ValueError("investor_share must be between 0 and 1")
    
    if invested_amount < 0:
        raise ValueError("invested_amount cannot be negative")
    
    pv = calculate_dcf(cash_flows, discount_rate)
    tv = terminal_value(cash_flows[-1], growth_rate, discount_rate)
    
    if tv is None:
        raise ValueError(f"terminal_value cannot be calculated: growth_rate ({growth_rate}) >= discount_rate ({discount_rate})")
    
    ev = exit_valuation(pv, tv)
    roi = exit_return_on_investment(ev, investor_share, invested_amount)
    
    return {
        'pv_cashflows': pv,
        'terminal_value': tv,
        'exit_valuation': ev,
        'investor_roi': roi
    }
