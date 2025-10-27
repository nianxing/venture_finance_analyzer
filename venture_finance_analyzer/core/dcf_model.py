"""dcf_model.py - DCF and exit helpers"""

def calculate_dcf(cash_flows, discount_rate):
    """
    计算现金流折现值
    
    Args:
        cash_flows: 现金流列表
        discount_rate: 折现率
    
    Returns:
        折现后的现值
    """
    if not cash_flows:
        raise ValueError("cash_flows cannot be empty")
    
    if discount_rate < 0:
        raise ValueError("discount_rate must be non-negative")
    
    pv = 0.0
    for t, cf in enumerate(cash_flows, start=1):
        pv += cf / ((1 + discount_rate) ** t)
    
    return round(pv, 2)


def terminal_value(last_cf, growth_rate, discount_rate):
    """
    计算终值（永续增长模型）
    
    Args:
        last_cf: 最后一期现金流
        growth_rate: 永续增长率
        discount_rate: 折现率
    
    Returns:
        终值，如果参数不合理返回 None
    """
    if growth_rate < 0:
        raise ValueError("growth_rate cannot be negative")
    
    if discount_rate <= growth_rate:
        # 永续增长率不能大于或等于折现率
        return None
    
    tv = last_cf * (1 + growth_rate) / (discount_rate - growth_rate)
    return round(tv, 2)


def exit_valuation(pv_cash_flows, terminal_val):
    """
    计算退出估值
    
    Args:
        pv_cash_flows: 现金流现值
        terminal_val: 终值
    
    Returns:
        总估值
    """
    if terminal_val is None:
        raise ValueError("terminal_val cannot be None")
    
    return round(pv_cash_flows + terminal_val, 2)


def exit_return_on_investment(exit_value, investor_share, invested_amount):
    """
    计算投资回报率
    
    Args:
        exit_value: 退出估值
        investor_share: 投资者持股比例
        invested_amount: 投资金额
    
    Returns:
        ROI (投资回报率)，如果投资额为0则返回 None
    """
    if exit_value < 0:
        raise ValueError("exit_value cannot be negative")
    
    if not (0 <= investor_share <= 1):
        raise ValueError("investor_share must be between 0 and 1")
    
    if invested_amount < 0:
        raise ValueError("invested_amount cannot be negative")
    
    if invested_amount == 0:
        return None
    
    proceeds = exit_value * investor_share
    roi = (proceeds - invested_amount) / invested_amount
    
    return round(roi, 4)
