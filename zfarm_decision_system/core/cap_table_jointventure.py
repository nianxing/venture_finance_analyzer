"""cap_table_jointventure.py - JV equity simulator"""
import pandas as pd

def simulate_jv_equity(initial_investments: dict, rounds: list):
    """
    模拟合资企业股权稀释
    
    Args:
        initial_investments: 初始投资 {'ag_inno': x, 'partner': y, 'grant': z}
        rounds: 融资轮次列表
    
    Returns:
        DataFrame with JV dilution details
    """
    # 参数验证
    if not isinstance(initial_investments, dict):
        raise TypeError("initial_investments must be a dict")
    
    if initial_investments and not isinstance(rounds, list):
        raise TypeError("rounds must be a list")
    
    total_initial = sum(initial_investments.values())
    
    if total_initial <= 0:
        raise ValueError("Total initial investment must be positive")
    
    ag_pct = initial_investments.get('ag_inno', 0) / total_initial
    partner_pct = initial_investments.get('partner', 0) / total_initial
    grant_pct = initial_investments.get('grant', 0) / total_initial
    
    records = []
    current_total = total_initial
    
    for idx, r in enumerate(rounds):
        # 验证每轮投资数据
        if not isinstance(r, dict):
            raise TypeError(f"Investment round {idx} must be a dict")
        
        amt = r.get('amount', 0)
        if amt <= 0:
            raise ValueError(f"Investment amount for round {idx} must be positive")
        
        round_name = r.get('round', f'Round_{idx+1}')
        
        post = current_total + amt
        new_investor_pct = amt / post
        
        ag_pct *= (1 - new_investor_pct)
        partner_pct *= (1 - new_investor_pct)
        grant_pct *= (1 - new_investor_pct)
        
        records.append({
            'round': round_name,
            'pre_money': round(current_total, 2),
            'investment': round(amt, 2),
            'post_money': round(post, 2),
            'ag_inno_pct': round(ag_pct, 4),
            'partner_pct': round(partner_pct, 4),
            'grant_pct': round(grant_pct, 4),
            'external_pct': round(1 - (ag_pct + partner_pct + grant_pct), 4)
        })
        
        current_total = post
    
    return pd.DataFrame(records)
