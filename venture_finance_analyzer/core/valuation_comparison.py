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

        partner_return = (post_money - total_investment) * equity_pct
        partner_returns[partner] = {
            'equity_percentage': equity_pct * 100,
            'return_amount': partner_return,
            'return_percentage': (partner_return / (post_money - total_investment)) * 100 if post_money > total_investment else 0
        }

    # 计算投资方总收益
    investor_return = post_money - total_investment
    investor_roi_pct = (investor_return / total_investment) * 100 if total_investment > 0 else 0

    return {
        'pre_money_valuation': pre_money,
        'post_money_valuation': post_money,
        'total_investment': total_investment,
        'valuation_multiple': valuation_multiple,
        'investor_roi_multiple': roi_multiple,
        'investor_roi_percentage': investor_roi_pct,
        'investor_total_return': investor_return,
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
            '项目': f'{partner} - 收益金额',
            '数值': data['return_amount'],
            '单位': '万元',
            '说明': f'{partner}从投资中获得的收益'
        })

        records.append({
            '项目': f'{partner} - 收益占比',
            '数值': data['return_percentage'],
            '单位': '%',
            '说明': f'{partner}在总收益中的占比'
        })

    return pd.DataFrame(records)
