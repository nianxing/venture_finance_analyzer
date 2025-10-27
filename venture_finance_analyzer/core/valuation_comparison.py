"""
valuation_comparison.py - 投前/投后估值对比和收益计算模块
"""
import pandas as pd
from typing import Dict, List, Optional


def calculate_valuation_comparison(
    pre_money: float,
    post_money: float,
    investment_rounds: List[Dict],
    partner_equity_splits: Dict[str, float]
) -> Dict:
    """
    计算投前/投后估值对比和合伙人收益

    Args:
        pre_money: 初始投前估值
        post_money: 最终投后估值
        investment_rounds: 投资轮次列表，每个包含轮次名称、投资额等信息
        partner_equity_splits: 合伙人股权分配比例

    Returns:
        包含估值对比和收益计算结果的字典
    """
    # 参数验证
    if pre_money <= 0 or post_money <= 0:
        raise ValueError("估值必须为正数")

    if post_money < pre_money:
        raise ValueError("投后估值不能低于投前估值")

    # 计算总投资额
    total_investment = sum(round['amount'] for round in investment_rounds)

    # 计算估值倍数
    valuation_multiple = post_money / pre_money if pre_money > 0 else 0

    # 计算投资回报倍数
    roi_multiple = (post_money - total_investment) / total_investment if total_investment > 0 else 0

    # 计算各合伙人的收益分配
    partner_returns = {}
    for partner, equity_pct in partner_equity_splits.items():
        if not (0 <= equity_pct <= 1):
            raise ValueError(f"合伙人 {partner} 的股权比例必须在0-1之间")

        # 股权价值 = 投后估值 × 股权比例
        equity_value = post_money * equity_pct
        
        # 对于合伙人（假设没有投资成本，或成本很少），收益=股权价值
        # 这可以根据实际需求调整
        partner_return = equity_value
        return_percentage = (equity_value / post_money) * 100
        
        partner_returns[partner] = {
            'equity_percentage': equity_pct * 100,
            'equity_value': equity_value,
            'return_amount': partner_return,
            'return_percentage': return_percentage
        }

    # 计算投资方整体收益
    # 如果所有股权都分配给了合伙人，则说明投资者在合伙人列表中
    # 这里计算的是所有投资者作为一个整体的表现
    total_equity_allocated = sum(partner_equity_splits.values())
    investor_equity_pct = 1 - total_equity_allocated if total_equity_allocated < 1 else 0
    investor_equity_value = post_money * investor_equity_pct
    investor_return = investor_equity_value - total_investment if investor_equity_pct > 0 else 0
    investor_roi_pct = (investor_return / total_investment) * 100 if total_investment > 0 else 0
    
    # 如果所有股权都已分配，计算总体的ROI（假设投资者获得部分股权价值）
    if total_equity_allocated >= 1:
        # 在这种情况下，基于投后估值和投资额计算理论ROI
        investor_equity_value = post_money - sum(data['equity_value'] for data in partner_returns.values())
        investor_return = post_money - total_investment
        investor_roi_pct = ((post_money - total_investment) / total_investment) * 100 if total_investment > 0 else 0

    return {
        'pre_money_valuation': pre_money,
        'post_money_valuation': post_money,
        'total_investment': total_investment,
        'valuation_multiple': valuation_multiple,
        'investor_roi_multiple': roi_multiple,
        'investor_roi_percentage': investor_roi_pct,
        'investor_total_return': investor_return,
        'investor_equity_value': investor_equity_value,
        'investor_equity_percentage': investor_equity_pct * 100,
        'partner_returns': partner_returns,
        'investment_rounds': investment_rounds
    }


def generate_valuation_comparison_table(comparison_data: Dict) -> pd.DataFrame:
    """
    生成估值对比分析表格

    Args:
        comparison_data: 估值对比数据

    Returns:
        包含详细分析结果的DataFrame
    """
    records = []

    # 基本信息
    records.append({
        '项目': '投前估值',
        '数值': comparison_data['pre_money_valuation'],
        '单位': '万元',
        '说明': '初始公司估值'
    })

    records.append({
        '项目': '投后估值',
        '数值': comparison_data['post_money_valuation'],
        '单位': '万元',
        '说明': '最终公司估值'
    })

    records.append({
        '项目': '总投资额',
        '数值': comparison_data['total_investment'],
        '单位': '万元',
        '说明': '所有轮次投资总额'
    })

    records.append({
        '项目': '估值倍数',
        '数值': comparison_data['valuation_multiple'],
        '单位': '倍',
        '说明': '投后估值相对于投前估值的倍数'
    })

    records.append({
        '项目': '投资回报倍数',
        '数值': comparison_data['investor_roi_multiple'],
        '单位': '倍',
        '说明': '投资额相对于投资成本的回报倍数'
    })

    records.append({
        '项目': '投资ROI',
        '数值': comparison_data['investor_roi_percentage'],
        '单位': '%',
        '说明': '投资回报率百分比'
    })

    # 各投资轮次详情
    for i, round_info in enumerate(comparison_data['investment_rounds']):
        records.append({
            '项目': f'轮次 {round_info["round"]}',
            '数值': round_info['amount'],
            '单位': '万元',
            '说明': f'第{i+1}轮投资额'
        })

    # 合伙人收益详情
    for partner, data in comparison_data['partner_returns'].items():
        records.append({
            '项目': f'{partner} - 股权比例',
            '数值': data['equity_percentage'],
            '单位': '%',
            '说明': f'{partner}持股比例'
        })

        records.append({
            '项目': f'{partner} - 股权价值',
            '数值': data['equity_value'],
            '单位': '万元',
            '说明': f'{partner}的股权现值'
        })

        records.append({
            '项目': f'{partner} - 收益占比',
            '数值': data['return_percentage'],
            '单位': '%',
            '说明': f'{partner}在总价值中的占比'
        })

    return pd.DataFrame(records)
