"""cap_table_main.py - parent company dilution simulator"""
import pandas as pd

def simulate_equity_dilution(pre_money: float, investments: list):
    """
    模拟母公司股权稀释
    
    Args:
        pre_money: 初始估值（万）
        investments: 融资轮次列表，每个元素包含 'amount' 和 'round'
    
    Returns:
        DataFrame with dilution details
    """
    # 参数验证
    if pre_money <= 0:
        raise ValueError("pre_money must be positive")
    
    if not investments:
        return pd.DataFrame(columns=['round', 'pre_money', 'investment', 'post_money', 'founders_pct', 'new_investor_pct'])
    
    if not isinstance(investments, list):
        raise TypeError("investments must be a list")
    
    records = []
    current_post = pre_money
    founders_pct = 1.0
    
    for idx, r in enumerate(investments):
        # 验证每轮投资数据
        if not isinstance(r, dict):
            raise TypeError(f"Investment round {idx} must be a dict")
        
        amount = r.get('amount', 0)
        if amount <= 0:
            raise ValueError(f"Investment amount for round {idx} must be positive")
        
        round_name = r.get('round', f'Round_{idx+1}')
        
        post_money = current_post + amount
        new_investor_pct = amount / post_money
        founders_pct = founders_pct * (1 - new_investor_pct)
        
        records.append({
            'round': round_name,
            'pre_money': round(current_post, 2),
            'investment': round(amount, 2),
            'post_money': round(post_money, 2),
            'founders_pct': round(founders_pct, 4),
            'new_investor_pct': round(new_investor_pct, 4)
        })
        
        current_post = post_money
    
    return pd.DataFrame(records)
