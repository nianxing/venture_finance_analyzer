"""
Venture Finance Analyzer - Web Application
Flask backend for interactive analysis
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from core.cap_table_main import simulate_equity_dilution
from core.cap_table_jointventure import simulate_jv_equity
from core.exit_analysis import analyze_exit
from core.montecarlo_risk import monte_carlo_exit_analysis
from core.valuation_comparison import calculate_valuation_comparison, generate_valuation_comparison_table
from core.equity_returns import simulate_multi_round_equity_dilution, generate_equity_returns_table, calculate_partner_contribution_analysis
import pandas as pd
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析API"""
    try:
        print("\n" + "="*50)
        print("收到API请求")
        print("="*50)
        data = request.json
        print(f"请求数据: {data}")
        
        results = {}
        
        # 1. 母公司稀释分析
        if 'parent_dilution' in data:
            print("处理母公司稀释分析...")
            parent_data = data['parent_dilution']
            print(f"parent_data: {parent_data}")
            
            # 支持新格式：rounds_data（包含完整轮次信息）
            if 'rounds_data' in parent_data:
                print("使用新格式 rounds_data")
                rounds_data = parent_data['rounds_data']
                initial_pre_money = parent_data.get('pre_money')
                print(f"rounds_data: {rounds_data}")
                print(f"initial_pre_money: {initial_pre_money}")
                df = simulate_equity_dilution(
                    initial_pre_money=initial_pre_money,
                    rounds_data=rounds_data
                )
                print(f"计算结果 DataFrame:\n{df}")
            # 兼容旧格式：pre_money + rounds
            else:
                parent_pre = float(parent_data.get('pre_money', 0))
                rounds = parent_data.get('rounds', [])
                df = simulate_equity_dilution(
                    initial_pre_money=parent_pre,
                    investments=rounds
                )
            
            results['parent_dilution'] = {
                'data': df.to_dict('records'),
                'final_dilution': float(df['founders_pct'].iloc[-1]) if not df.empty else 100
            }
            print(f"返回结果: {results['parent_dilution']}")
        
        # 2. JV稀释分析
        if 'jv_dilution' in data:
            initial_inv = data['jv_dilution']['initial_investments']
            rounds_jv = data['jv_dilution']['rounds']
            df = simulate_jv_equity(initial_inv, rounds_jv)
            results['jv_dilution'] = {
                'data': df.to_dict('records'),
                'final_ownership': df.iloc[-1].to_dict() if not df.empty else {}
            }
        
        # 3. 退出分析
        if 'exit_analysis' in data:
            cash_flows = [float(x) for x in data['exit_analysis']['cash_flows']]
            discount_rate = float(data['exit_analysis']['discount_rate'])
            growth_rate = float(data['exit_analysis']['growth_rate'])
            investor_share = float(data['exit_analysis']['investor_share'])
            invested_amount = float(data['exit_analysis']['invested_amount'])
            
            res = analyze_exit(cash_flows, discount_rate, growth_rate, investor_share, invested_amount)
            results['exit_analysis'] = res
            
            # 4. 蒙特卡洛分析
            if 'run_montecarlo' in data and data['run_montecarlo']:
                mc_trials = int(data.get('montecarlo_trials', 10000))
                cf_volatility = float(data.get('cf_volatility', 0.2))
                
                mc_results = monte_carlo_exit_analysis(
                    cash_flows, discount_rate, growth_rate, investor_share, invested_amount,
                    trials=mc_trials, cf_volatility=cf_volatility
                )
                results['montecarlo'] = mc_results

        # 5. 估值对比分析
        if 'valuation_comparison' in data:
            pre_money = float(data['valuation_comparison']['pre_money'])
            post_money = float(data['valuation_comparison']['post_money'])
            investment_rounds = data['valuation_comparison']['investment_rounds']
            partner_equity_splits = data['valuation_comparison']['partner_equity_splits']

            comparison_result = calculate_valuation_comparison(
                pre_money, post_money, investment_rounds, partner_equity_splits
            )
            comparison_table = generate_valuation_comparison_table(comparison_result)

            results['valuation_comparison'] = {
                'data': comparison_result,
                'table': comparison_table.to_dict('records')
            }

        # 6. 股比和收益分析
        if 'equity_returns' in data:
            initial_valuation = float(data['equity_returns']['initial_valuation'])
            investment_rounds = data['equity_returns']['investment_rounds']
            initial_partners = data['equity_returns']['initial_partners']
            new_investors_per_round = data['equity_returns'].get('new_investors_per_round', {})

            equity_result = simulate_multi_round_equity_dilution(
                initial_valuation, investment_rounds, initial_partners, new_investors_per_round
            )
            equity_table = generate_equity_returns_table(equity_result)

            results['equity_returns'] = {
                'data': equity_result,
                'table': equity_table.to_dict('records')
            }

        response_data = {
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        print(f"返回响应: {response_data}")
        print("="*50 + "\n")
        return jsonify(response_data)
    
    except Exception as e:
        import traceback
        print(f"\n错误: {str(e)}")
        print(f"错误详情:\n{traceback.format_exc()}")
        print("="*50 + "\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/export/<analysis_type>', methods=['POST'])
def export_analysis(analysis_type):
    """导出分析结果"""
    try:
        data = request.json
        
        # 这里可以实现导出Excel/PDF等功能
        return jsonify({
            'success': True,
            'message': 'Export functionality coming soon'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Venture Finance Analyzer - Web Interface")
    print("="*50)
    print("\nStarting server...")
    print("Open your browser and visit: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

