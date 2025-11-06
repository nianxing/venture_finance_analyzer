"""cap_table_main.py - parent company dilution simulator"""
import pandas as pd
from typing import List, Dict, Optional


def calculate_round_values(
    pre_money: Optional[float] = None,
    post_money: Optional[float] = None,
    investment: Optional[float] = None,
    investor_pct: Optional[float] = None
) -> Dict[str, float]:
    """
    根据任意给定的值计算其他值（支持反向计算）
    
    Args:
        pre_money: 投前估值（万）
        post_money: 投后估值（万）
        investment: 投资额（万）
        investor_pct: 投资者股权比例（0-100）
    
    Returns:
        包含所有计算值的字典
    """
    # 优先级1: 如果提供了股权比例和投资额，计算投后和投前
    if investor_pct is not None and investor_pct > 0 and investment is not None and investment > 0:
        post_money = investment / (investor_pct / 100)
        pre_money = post_money - investment
    
    # 优先级2: 如果提供了股权比例和投后，计算投资额和投前
    elif investor_pct is not None and investor_pct > 0 and post_money is not None and post_money > 0:
        investment = post_money * (investor_pct / 100)
        pre_money = post_money - investment
    
    # 优先级3: 如果提供了投前和投资额，计算投后
    elif pre_money is not None and pre_money > 0 and investment is not None and investment > 0:
        post_money = pre_money + investment
    
    # 优先级4: 如果提供了投后和投资额，计算投前
    elif post_money is not None and post_money > 0 and investment is not None and investment > 0:
        pre_money = post_money - investment
    
    # 优先级5: 如果提供了投后和投前，计算投资额
    elif post_money is not None and post_money > 0 and pre_money is not None and pre_money > 0:
        investment = post_money - pre_money
    
    # 计算股权比例（如果还没有计算）
    if investor_pct is None and post_money is not None and post_money > 0 and investment is not None:
        investor_pct = (investment / post_money) * 100
    
    return {
        'pre_money': pre_money or 0.0,
        'post_money': post_money or 0.0,
        'investment': investment or 0.0,
        'investor_pct': investor_pct or 0.0
    }


def simulate_equity_dilution(
    initial_pre_money: Optional[float] = None,
    investments: Optional[List[Dict]] = None,
    rounds_data: Optional[List[Dict]] = None
):
    """
    模拟母公司股权稀释（改进版：支持灵活输入）
    
    Args:
        initial_pre_money: 初始投前估值（万）- 可选，如果rounds_data中提供了第一轮的pre_money则不需要
        investments: 融资轮次列表（旧格式兼容），每个元素包含 'amount' 和 'round'
        rounds_data: 融资轮次列表（新格式），每个元素可包含：
            - 'round': 轮次名称
            - 'pre_money': 投前估值（万）
            - 'post_money': 投后估值（万）
            - 'investment': 投资额（万）
            - 'investor_pct': 投资者股权比例（0-100）
            - 'locked': 字典，指定哪些字段被锁定（如 {'pre_money': True}）
    
    Returns:
        DataFrame with dilution details
    """
    # 兼容旧格式
    if investments and not rounds_data:
        rounds_data = []
        current_pre = initial_pre_money or 0
        for r in investments:
            rounds_data.append({
                'round': r.get('round', 'Round'),
                'pre_money': current_pre,
                'investment': r.get('amount', 0)
            })
            current_pre = current_pre + r.get('amount', 0)
    
    if not rounds_data:
        return pd.DataFrame(columns=['round', 'pre_money', 'investment', 'post_money', 'founders_pct', 'new_investor_pct'])
    
    records = []
    previous_post_money = initial_pre_money if initial_pre_money else None
    founders_pct = 1.0
    
    for idx, round_data in enumerate(rounds_data):
        if not isinstance(round_data, dict):
            raise TypeError(f"Round {idx} must be a dict")
        
        round_name = round_data.get('round', f'Round_{idx+1}')
        locked = round_data.get('locked', {})
        
        # 读取输入值
        pre_money = round_data.get('pre_money')
        post_money = round_data.get('post_money')
        investment = round_data.get('investment')
        investor_pct = round_data.get('investor_pct')
        
        # 如果投前估值为空且不是第一轮，从上一轮的投后估值继承
        if pre_money is None and idx > 0 and previous_post_money is not None:
            pre_money = previous_post_money
        
        # 如果投前估值为空且是第一轮，使用initial_pre_money
        if pre_money is None and idx == 0 and initial_pre_money:
            pre_money = initial_pre_money
        
        # 计算所有值（考虑锁定状态）
        calculated = calculate_round_values(
            pre_money=pre_money if not locked.get('pre_money') else None,
            post_money=post_money if not locked.get('post_money') else None,
            investment=investment if not locked.get('investment') else None,
            investor_pct=investor_pct if not locked.get('investor_pct') else None
        )
        
        # 如果字段被锁定，使用原始值（优先保留锁定值）
        if locked.get('pre_money') and pre_money is not None:
            calculated['pre_money'] = pre_money
        if locked.get('post_money') and post_money is not None:
            calculated['post_money'] = post_money
        if locked.get('investment') and investment is not None:
            calculated['investment'] = investment
        if locked.get('investor_pct') and investor_pct is not None:
            calculated['investor_pct'] = investor_pct
        
        # 确保投前+投资额=投后（但不要覆盖锁定的字段）
        # 如果post_money未锁定，且pre_money和investment都有值，则计算post_money
        if not locked.get('post_money') and calculated['pre_money'] > 0 and calculated['investment'] > 0:
            calculated['post_money'] = calculated['pre_money'] + calculated['investment']
        # 如果post_money已锁定，但pre_money或investment未锁定，则根据post_money计算它们
        elif locked.get('post_money') and calculated['post_money'] > 0:
            if not locked.get('pre_money') and calculated['investment'] > 0:
                calculated['pre_money'] = calculated['post_money'] - calculated['investment']
            elif not locked.get('investment') and calculated['pre_money'] > 0:
                calculated['investment'] = calculated['post_money'] - calculated['pre_money']
        
        # 计算股权比例（但不要覆盖锁定的investor_pct）
        if not locked.get('investor_pct') and calculated['post_money'] > 0 and calculated['investment'] >= 0:
            calculated['investor_pct'] = (calculated['investment'] / calculated['post_money']) * 100
        # 如果investor_pct已锁定，但investment未锁定，则根据investor_pct计算investment
        elif locked.get('investor_pct') and calculated['investor_pct'] > 0 and calculated['post_money'] > 0 and not locked.get('investment'):
            calculated['investment'] = calculated['post_money'] * (calculated['investor_pct'] / 100)
            # 重新计算pre_money（如果未锁定）
            if not locked.get('pre_money'):
                calculated['pre_money'] = calculated['post_money'] - calculated['investment']
        
        # 计算创始人持股（累积稀释）
        if calculated['post_money'] > 0:
            dilution_factor = (100 - calculated['investor_pct']) / 100
            founders_pct = founders_pct * dilution_factor
        
        records.append({
            'round': round_name,
            'pre_money': round(calculated['pre_money'], 2),
            'investment': round(calculated['investment'], 2),
            'post_money': round(calculated['post_money'], 2),
            'founders_pct': round(founders_pct * 100, 2),  # 转换为百分比
            'new_investor_pct': round(calculated['investor_pct'], 2)
        })
        
        previous_post_money = calculated['post_money']
    
    return pd.DataFrame(records)
