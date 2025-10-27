"""
equity_returns.py - 不同合伙人和投资方在不同轮次的股比和收益计算模块
"""
import pandas as pd
from typing import Dict, List


def simulate_multi_round_equity_dilution(
    initial_valuation: float,
    investment_rounds: List[Dict],
    initial_partners: Dict[str, float],
    new_investors_per_round: Dict[str, float]
) -> Dict:
    """
    模拟多轮次融资中的股权稀释和收益计算

    Args:
        initial_valuation: 初始估值
        investment_rounds: 投资轮次列表，包含轮次名称和投资额
        initial_partners: 初始合伙人及其股权比例
        new_investors_per_round: 每轮新投资者的股权比例

    Returns:
        包含完整模拟结果的字典
    """
    # 参数验证
    if initial_valuation <= 0:
        raise ValueError("初始估值必须为正数")

    if sum(initial_partners.values()) > 1:
        raise ValueError("初始合伙人股权比例总和不能超过100%")

    # 初始化
    current_valuation = initial_valuation
    partner_equity = initial_partners.copy()
    remaining_equity = 1.0 - sum(initial_partners.values())

    records = []
    total_investment = 0

    # 模拟每轮投资
    for i, round_info in enumerate(investment_rounds):
        investment_amount = round_info['amount']
        round_name = round_info['round']

        if investment_amount <= 0:
            raise ValueError(f"第{i+1}轮投资额必须为正数")

        # 计算投后估值
        post_money_valuation = current_valuation + investment_amount

        # 计算新投资者的股权比例
        new_investor_equity = investment_amount / post_money_valuation

        # 验证新投资者比例
        if round_name in new_investors_per_round:
            specified_equity = new_investors_per_round[round_name]
            if abs(new_investor_equity - specified_equity) > 0.001:
                # 如果用户指定了特定的股权比例，使用用户指定的
                new_investor_equity = specified_equity
                # 重新计算投资额
                investment_amount = current_valuation * new_investor_equity / (1 - new_investor_equity)

        # 计算稀释后的股权比例
        dilution_factor = 1 - new_investor_equity

        # 更新合伙人股权（按比例稀释）
        for partner in partner_equity:
            partner_equity[partner] *= dilution_factor

        # 更新剩余股权（用于新合伙人）
        remaining_equity *= dilution_factor

        # 添加新投资者
        partner_equity[f"投资者-{round_name}"] = new_investor_equity

        # 计算本轮投资后的总估值和总投资额
        total_investment += investment_amount
        current_valuation = post_money_valuation

        # 记录本轮结果
        round_record = {
            '轮次': round_name,
            '投资额': investment_amount,
            '投前估值': current_valuation - investment_amount,
            '投后估值': current_valuation,
            '新投资者股权': new_investor_equity * 100,
            '总投资额': total_investment
        }

        # 添加各合伙人的股权比例
        for partner, equity in partner_equity.items():
            round_record[f"{partner}_股权"] = equity * 100

        records.append(round_record)

    # 计算最终收益分配（假设退出时按当前估值退出）
    exit_valuation = current_valuation
    total_return = exit_valuation - total_investment

    # 计算每个参与者的收益
    participant_returns = {}
    for participant, equity in partner_equity.items():
        return_amount = total_return * equity
        roi_percentage = (return_amount / total_investment) * 100 if total_investment > 0 else 0

        participant_returns[participant] = {
            '最终股权比例': equity * 100,
            '收益金额': return_amount,
            '投资回报率': roi_percentage,
            '投资成本': 0,  # 这里可以根据实际情况设置初始投资成本
            '净收益': return_amount
        }

    return {
        'simulation_data': records,
        'final_equity_distribution': partner_equity,
        'participant_returns': participant_returns,
        'total_investment': total_investment,
        'exit_valuation': exit_valuation,
        'total_return': total_return,
        'roi_percentage': (total_return / total_investment) * 100 if total_investment > 0 else 0
    }


def generate_equity_returns_table(equity_data: Dict) -> pd.DataFrame:
    """
    生成股权收益分析表格

    Args:
        equity_data: 股权收益数据

    Returns:
        包含详细收益分析的DataFrame
    """
    records = []

    # 添加汇总信息
    records.append({
        '项目': '总投资额',
        '数值': equity_data['total_investment'],
        '单位': '万元',
        '说明': '所有轮次投资总额'
    })

    records.append({
        '项目': '退出估值',
        '数值': equity_data['exit_valuation'],
        '单位': '万元',
        '说明': '假设退出时的公司估值'
    })

    records.append({
        '项目': '总收益',
        '数值': equity_data['total_return'],
        '单位': '万元',
        '说明': '退出时相对于总投资的收益'
    })

    records.append({
        '项目': '整体ROI',
        '数值': equity_data['roi_percentage'],
        '单位': '%',
        '说明': '整体投资回报率'
    })

    # 添加每个参与者的详细收益
    for participant, data in equity_data['participant_returns'].items():
        records.append({
            '项目': f'{participant} - 最终股权',
            '数值': data['最终股权比例'],
            '单位': '%',
            '说明': f'{participant}的最终持股比例'
        })

        records.append({
            '项目': f'{participant} - 收益金额',
            '数值': data['收益金额'],
            '单位': '万元',
            '说明': f'{participant}从退出中获得的收益'
        })

        records.append({
            '项目': f'{participant} - 回报率',
            '数值': data['投资回报率'],
            '单位': '%',
            '说明': f'{participant}的投资回报率'
        })

    return pd.DataFrame(records)


def calculate_partner_contribution_analysis(
    initial_investments: Dict[str, float],
    investment_rounds: List[Dict],
    exit_valuation: float
) -> Dict:
    """
    分析各合伙人的贡献和收益分配

    Args:
        initial_investments: 各合伙人的初始投资额
        investment_rounds: 投资轮次信息
        exit_valuation: 退出时估值

    Returns:
        各合伙人贡献分析结果
    """
    total_initial_investment = sum(initial_investments.values())
    total_investment = total_initial_investment + sum(r['amount'] for r in investment_rounds)

    # 计算各合伙人的投资比例
    partner_investment_ratios = {}
    for partner, amount in initial_investments.items():
        partner_investment_ratios[partner] = amount / total_initial_investment

    # 计算退出时各方的价值
    total_return = exit_valuation - total_investment

    partner_analysis = {}
    for partner, initial_amount in initial_investments.items():
        # 按投资比例计算的理论收益
        theoretical_return = total_return * (initial_amount / total_initial_investment)

        # 按当前股权比例计算的实际收益
        current_equity_ratio = partner_investment_ratios[partner]
        actual_return = total_return * current_equity_ratio

        partner_analysis[partner] = {
            '初始投资': initial_amount,
            '投资比例': partner_investment_ratios[partner] * 100,
            '理论收益': theoretical_return,
            '实际收益': actual_return,
            '收益差额': actual_return - theoretical_return,
            '回报倍数': (actual_return / initial_amount) if initial_amount > 0 else 0
        }

    return {
        'partner_analysis': partner_analysis,
        'total_initial_investment': total_initial_investment,
        'total_investment': total_investment,
        'exit_valuation': exit_valuation,
        'total_return': total_return
    }
