// Venture Finance Analyzer - Frontend Logic

// Tab切换
function switchTab(index) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-button');
    
    tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === index);
    });
    
    buttons.forEach((btn, i) => {
        btn.classList.toggle('active', i === index);
    });
}

// 添加融资轮次
function addRound(type) {
    const roundsDiv = document.getElementById(type + '-rounds');
    const newRound = document.createElement('div');
    newRound.className = 'round-item';
    newRound.innerHTML = `
        <input type="text" placeholder="轮次名称">
        <input type="number" placeholder="投资额(万元)" value="0" step="100">
        <button class="btn btn-danger" onclick="this.parentElement.remove()">删除</button>
    `;
    roundsDiv.appendChild(newRound);
}

// 显示加载状态
function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

// 母公司稀释分析
async function analyzeParent() {
    showLoading();
    
    try {
        const preMoney = parseFloat(document.getElementById('parent_pre_money').value);
        const rounds = Array.from(document.querySelectorAll('#parent-rounds .round-item')).map(item => {
            const inputs = item.querySelectorAll('input');
            return {
                round: inputs[0].value || 'Round',
                amount: parseFloat(inputs[1].value)
            };
        });
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                parent_dilution: { pre_money: preMoney, rounds: rounds }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayParentResults(data.results.parent_dilution);
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示母公司结果
function displayParentResults(data) {
    const resultsDiv = document.getElementById('parent-results');
    
    let html = '<div class="result-card"><h4>分析结果</h4>';
    html += `<div class="stats-grid">
        <div class="stat-card">
            <h5>最终创始人持股</h5>
            <div class="value">${data.final_dilution.toFixed(2)}%</div>
        </div>
    </div>`;
    
    // 表格
    html += '<table><thead><tr><th>轮次</th><th>投前估值</th><th>投资额</th><th>投后估值</th><th>创始人持股</th><th>新投资者持股</th></tr></thead><tbody>';
    
    data.data.forEach(row => {
        html += `<tr>
            <td>${row.round}</td>
            <td>${row.pre_money.toFixed(0)}万</td>
            <td>${row.investment.toFixed(0)}万</td>
            <td>${row.post_money.toFixed(0)}万</td>
            <td>${(row.founders_pct * 100).toFixed(2)}%</td>
            <td>${(row.new_investor_pct * 100).toFixed(2)}%</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    // 图表
    html += '<div class="chart-container"><canvas id="parentChart"></canvas></div>';
    
    resultsDiv.innerHTML = html;
    
    // 绘制图表
    const ctx = document.getElementById('parentChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.data.map(r => r.round),
            datasets: [{
                label: '创始人持股比例',
                data: data.data.map(r => r.founders_pct * 100),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: '股权稀释趋势' }
            },
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { suffix: '%' } }
            }
        }
    });
}

// JV稀释分析
async function analyzeJV() {
    showLoading();
    
    try {
        const initialInv = {
            ag_inno: parseFloat(document.getElementById('jv_ag_inno').value),
            partner: parseFloat(document.getElementById('jv_partner').value),
            grant: parseFloat(document.getElementById('jv_grant').value)
        };
        
        const rounds = Array.from(document.querySelectorAll('#jv-rounds .round-item')).map(item => {
            const inputs = item.querySelectorAll('input');
            return {
                round: inputs[0].value || 'Round',
                amount: parseFloat(inputs[1].value)
            };
        });
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                jv_dilution: { initial_investments: initialInv, rounds: rounds }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayJVResults(data.results.jv_dilution);
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示JV结果
function displayJVResults(data) {
    const resultsDiv = document.getElementById('jv-results');
    
    const final = data.final_ownership;
    
    let html = '<div class="result-card"><h4>分析结果</h4>';
    html += `<div class="stats-grid">
        <div class="stat-card">
            <h5>AgInno持股</h5>
            <div class="value">${(final.ag_inno_pct * 100).toFixed(2)}%</div>
        </div>
        <div class="stat-card">
            <h5>Partner持股</h5>
            <div class="value">${(final.partner_pct * 100).toFixed(2)}%</div>
        </div>
        <div class="stat-card">
            <h5>Grant持股</h5>
            <div class="value">${(final.grant_pct * 100).toFixed(2)}%</div>
        </div>
        <div class="stat-card">
            <h5>外部投资者</h5>
            <div class="value">${(final.external_pct * 100).toFixed(2)}%</div>
        </div>
    </div>`;
    
    // 表格
    html += '<table><thead><tr><th>轮次</th><th>投前估值</th><th>投资额</th><th>投后估值</th><th>AgInno</th><th>Partner</th><th>Grant</th><th>外部</th></tr></thead><tbody>';
    
    data.data.forEach(row => {
        html += `<tr>
            <td>${row.round}</td>
            <td>${row.pre_money.toFixed(0)}万</td>
            <td>${row.investment.toFixed(0)}万</td>
            <td>${row.post_money.toFixed(0)}万</td>
            <td>${(row.ag_inno_pct * 100).toFixed(2)}%</td>
            <td>${(row.partner_pct * 100).toFixed(2)}%</td>
            <td>${(row.grant_pct * 100).toFixed(2)}%</td>
            <td>${(row.external_pct * 100).toFixed(2)}%</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    
    // 图表
    html += '<div class="chart-container"><canvas id="jvChart"></canvas></div>';
    
    resultsDiv.innerHTML = html;
    
    // 绘制图表
    const ctx = document.getElementById('jvChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.data.map(r => r.round),
            datasets: [
                { label: 'AgInno', data: data.data.map(r => r.ag_inno_pct * 100), borderColor: '#28a745', tension: 0.4 },
                { label: 'Partner', data: data.data.map(r => r.partner_pct * 100), borderColor: '#17a2b8', tension: 0.4 },
                { label: 'Grant', data: data.data.map(r => r.grant_pct * 100), borderColor: '#ffc107', tension: 0.4 },
                { label: '外部投资者', data: data.data.map(r => r.external_pct * 100), borderColor: '#dc3545', tension: 0.4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: 'JV股权稀释趋势' } },
            scales: { y: { beginAtZero: true, ticks: { suffix: '%' } } }
        }
    });
}

// 退出估值分析
async function analyzeExit() {
    showLoading();
    
    try {
        const cashFlows = document.getElementById('cash_flows').value.split(',').map(x => parseFloat(x.trim()));
        const discountRate = parseFloat(document.getElementById('discount_rate').value);
        const growthRate = parseFloat(document.getElementById('growth_rate').value);
        const investorShare = parseFloat(document.getElementById('investor_share').value);
        const investedAmount = parseFloat(document.getElementById('invested_amount').value);
        const runMC = document.getElementById('run_montecarlo').checked;
        const mcTrials = parseInt(document.getElementById('montecarlo_trials').value);
        const cfVolatility = parseFloat(document.getElementById('cf_volatility').value);
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                exit_analysis: {
                    cash_flows: cashFlows,
                    discount_rate: discountRate,
                    growth_rate: growthRate,
                    investor_share: investorShare,
                    invested_amount: investedAmount
                },
                run_montecarlo: runMC,
                montecarlo_trials: mcTrials,
                cf_volatility: cfVolatility
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExitResults(data.results);
        } else {
            alert('分析失败: ' + data.error);
        }
    } catch (error) {
        alert('错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

// 显示退出分析结果
function displayExitResults(results) {
    const resultsDiv = document.getElementById('exit-results');
    
    const exit = results.exit_analysis;
    
    let html = '<div class="result-card"><h4>DCF估值结果</h4>';
    html += `<div class="stats-grid">
        <div class="stat-card">
            <h5>现金流现值</h5>
            <div class="value">${exit.pv_cashflows.toFixed(0)}万</div>
        </div>
        <div class="stat-card">
            <h5>终值</h5>
            <div class="value">${exit.terminal_value.toFixed(0)}万</div>
        </div>
        <div class="stat-card">
            <h5>退出估值</h5>
            <div class="value">${exit.exit_valuation.toFixed(0)}万</div>
        </div>
        <div class="stat-card">
            <h5>投资回报率</h5>
            <div class="value">${(exit.investor_roi * 100).toFixed(2)}%</div>
        </div>
    </div></div>`;
    
    // 蒙特卡洛结果
    if (results.montecarlo) {
        const mc = results.montecarlo;
        html += '<div class="result-card"><h4>蒙特卡洛风险分析</h4>';
        html += `<p>模拟次数: ${mc.trials_count}</p>`;
        html += '<div class="stats-grid">
            <div class="stat-card"><h5>估值均值</h5><div class="value">'+mc.mean_exit_value.toFixed(0)+'万</div></div>
            <div class="stat-card"><h5>估值中位数</h5><div class="value">'+mc.median_exit_value.toFixed(0)+'万</div></div>
            <div class="stat-card"><h5>估值10%分位</h5><div class="value">'+mc.p10_exit_value.toFixed(0)+'万</div></div>
            <div class="stat-card"><h5>估值90%分位</h5><div class="value">'+mc.p90_exit_value.toFixed(0)+'万</div></div>
            <div class="stat-card"><h5>ROI均值</h5><div class="value">'+(mc.mean_roi * 100).toFixed(2)+'%</div></div>
            <div class="stat-card"><h5>ROI中位数</h5><div class="value">'+(mc.median_roi * 100).toFixed(2)+'%</div></div>
            <div class="stat-card"><h5>ROI 10%分位</h5><div class="value">'+(mc.p10_roi * 100).toFixed(2)+'%</div></div>
            <div class="stat-card"><h5>ROI 90%分位</h5><div class="value">'+(mc.p90_roi * 100).toFixed(2)+'%</div></div>
        </div></div>';
    }
    
    resultsDiv.innerHTML = html;
}

