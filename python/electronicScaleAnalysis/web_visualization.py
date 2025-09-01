import os
import json
import webbrowser
from datetime import datetime
import csv_processor

class WebVisualizationGenerator:
    """生成称重数据可视化网页的工具类"""
    
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.current_dir, 'web_output')
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_html_page(self, statistics_data):
        """生成HTML页面"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>称重数据时间分布统计可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        
        .data-table {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .table-title {{
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }}
        
        tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .nav-tabs {{
            display: flex;
            border-bottom: 2px solid #dee2e6;
            margin-bottom: 20px;
        }}
        
        .nav-tab {{
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            color: #666;
            font-size: 1.1em;
            transition: all 0.3s ease;
        }}
        
        .nav-tab.active {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            font-weight: bold;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .summary-card h4 {{
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .summary-value {{
            font-size: 1.8em;
            font-weight: bold;
        }}
        
        /* 分页样式 */
        .pagination-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            gap: 10px;
        }}
        
        .pagination-info {{
            color: #666;
            font-size: 0.9em;
            margin: 0 15px;
        }}
        
        .pagination-btn {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            background: white;
            color: #333;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }}
        
        .pagination-btn:hover:not(:disabled) {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .pagination-btn:disabled {{
            background: #f5f5f5;
            color: #ccc;
            cursor: not-allowed;
            border-color: #e0e0e0;
        }}
        
        .pagination-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .pagination-input {{
            width: 60px;
            padding: 6px 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .pagination-input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            margin-bottom: 20px;
        }}
        
        .table-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .page-size-selector {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .page-size-selector select {{
            padding: 6px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            font-size: 0.9em;
        }}
        
        .page-size-selector select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        /* 异常分析样式 */
        .anomaly-tab-content {{
            display: none;
        }}
        
        .anomaly-tab-content.active {{
            display: block;
        }}
        
        .anomaly-severity {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .anomaly-severity.normal {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .anomaly-severity.mild {{
            background-color: #fff3cd;
            color: #856404;
        }}
        
        .anomaly-severity.severe {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .anomaly-severity.outlier {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .comparison-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .comparison-card {{
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #333;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .comparison-card h4 {{
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .comparison-value {{
            font-size: 1.8em;
            font-weight: bold;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .summary-stats {{
                grid-template-columns: 1fr;
            }}
            
            .nav-tabs {{
                flex-direction: column;
            }}
            
            
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ 称重数据时间分布统计</h1>
            <p>智能分析称重数据的每日、每周、每月统计信息</p>
        </div>
        
        <div class="content">
            <!-- 总体统计卡片 -->
            <div class="summary-stats">
                <div class="summary-card">
                    <h4>总称重次数</h4>
                    <div class="summary-value" id="total-count">-</div>
                </div>
                <div class="summary-card">
                    <h4>平均重量</h4>
                    <div class="summary-value" id="avg-weight">-</div>
                </div>
                <div class="summary-card">
                    <h4>重量标准差</h4>
                    <div class="summary-value" id="avg-std">-</div>
                </div>
                <div class="summary-card">
                    <h4>数据覆盖天数</h4>
                    <div class="summary-value" id="total-days">-</div>
                </div>
            </div>
            

            
            
            
            <!-- 详细数据表格 -->
            <div class="data-table">
                <div class="nav-tabs">
                    <button class="nav-tab active" onclick="showTab('daily')">📅 每日统计</button>
                    <button class="nav-tab" onclick="showTab('weekly')">📆 每周统计</button>
                    <button class="nav-tab" onclick="showTab('monthly')">🗓️ 每月统计</button>
                    <button class="nav-tab" onclick="showTab('weeklyCompare')">⚖️ 周内 vs 周末</button>
                    <button class="nav-tab" onclick="showTab('anomaly')">🚨 异常分析</button>
                </div>
                
                <div id="daily" class="tab-content active">
                    <div class="table-title">每日称重统计详情</div>
                    <div class="chart-wrapper">
                        <canvas id="dailyChart"></canvas>
                    </div>
                    <div id="daily-table"></div>
                </div>
                
                <div id="weekly" class="tab-content">
                    <div class="table-title">每周称重统计详情</div>
                    <div class="chart-wrapper">
                        <canvas id="weeklyChart"></canvas>
                    </div>
                    <div id="weekly-table"></div>
                </div>
                
                <div id="monthly" class="tab-content">
                    <div class="table-title">每月称重统计详情</div>
                    <div class="chart-wrapper">
                        <canvas id="monthlyChart"></canvas>
                    </div>
                    <div id="monthly-table"></div>
                </div>
                
                <div id="weeklyCompare" class="tab-content">
                    <div class="table-title">每周 周内(工作日) 与 周末 对比</div>
                    <div class="chart-container">
                        <div class="chart-title">📊 周内 vs 周末 称重次数对比</div>
                        <div class="chart-wrapper">
                            <canvas id="weeklyCompareCountChart"></canvas>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">⚖️ 周内 vs 周末 重量均值对比</div>
                        <div class="chart-wrapper">
                            <canvas id="weeklyCompareMeanChart"></canvas>
                        </div>
                    </div>
                    <div id="weekly-compare-table"></div>
                </div>
                
                <div id="anomaly" class="tab-content">
                    <div class="table-title">🚨 称重数据异常分析</div>
                    
                    <!-- 异常分析概览 -->
                    <div class="summary-stats" id="anomaly-summary">
                        <div class="summary-card">
                            <h4>总记录数</h4>
                            <div class="summary-value" id="total-records">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>Z-score异常率</h4>
                            <div class="summary-value" id="z-anomaly-rate">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>IQR异常率</h4>
                            <div class="summary-value" id="iqr-anomaly-rate">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>共同异常数</h4>
                            <div class="summary-value" id="common-anomalies">-</div>
                        </div>
                    </div>
                    
                    <!-- 异常分析图表 -->
                    <div class="chart-container">
                        <div class="chart-title">📊 异常检测方法对比</div>
                        <div class="chart-wrapper">
                            <canvas id="anomalyComparisonChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">📈 Z-score异常分布</div>
                        <div class="chart-wrapper">
                            <canvas id="zScoreDistributionChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 异常数据表格 -->
                    <div class="nav-tabs">
                        <button class="nav-tab active" onclick="showAnomalyTab('z-score')">Z-score异常</button>
                        <button class="nav-tab" onclick="showAnomalyTab('iqr')">IQR异常</button>
                        <button class="nav-tab" onclick="showAnomalyTab('comparison')">方法对比</button>
                    </div>
                    
                    <div id="z-score-anomalies" class="anomaly-tab-content active">
                        <div class="table-title">Z-score异常数据详情</div>
                        <div id="z-score-table"></div>
                    </div>
                    
                    <div id="iqr-anomalies" class="anomaly-tab-content">
                        <div class="table-title">IQR异常数据详情</div>
                        <div id="iqr-table"></div>
                    </div>
                    
                    <div id="comparison-anomalies" class="anomaly-tab-content">
                        <div class="table-title">异常检测方法对比分析</div>
                        <div id="comparison-table"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 数据变量
        let statisticsData = {json.dumps(statistics_data, ensure_ascii=False, default=str)};
        let anomalyData = null;
        
        // 分页配置
        const paginationConfig = {{
            pageSize: 20,
            maxVisiblePages: 5
        }};
        
        // 分页状态
        const paginationState = {{
            daily: {{ currentPage: 1, totalPages: 1 }},
            weekly: {{ currentPage: 1, totalPages: 1 }},
            monthly: {{ currentPage: 1, totalPages: 1 }},
            weeklyCompare: {{ currentPage: 1, totalPages: 1 }},
            zScore: {{ currentPage: 1, totalPages: 1 }},
            iqr: {{ currentPage: 1, totalPages: 1 }}
        }};
        
        // 分页工具函数
        function createPaginationHTML(tableId, currentPage, totalPages, totalItems) {{
            const startItem = (currentPage - 1) * paginationConfig.pageSize + 1;
            const endItem = Math.min(currentPage * paginationConfig.pageSize, totalItems);
            
            let paginationHTML = `
                <div class="table-controls">
                    <div class="page-size-selector">
                        <label>每页显示:</label>
                        <select onchange="changePageSize('${{tableId}}', this.value)">
                            <option value="10" ${{paginationConfig.pageSize === 10 ? 'selected' : ''}}>10</option>
                            <option value="20" ${{paginationConfig.pageSize === 20 ? 'selected' : ''}}>20</option>
                            <option value="50" ${{paginationConfig.pageSize === 50 ? 'selected' : ''}}>50</option>
                            <option value="100" ${{paginationConfig.pageSize === 100 ? 'selected' : ''}}>100</option>
                        </select>
                    </div>
                    <div class="pagination-info">
                        显示 ${{startItem}} - ${{endItem}} 条，共 ${{totalItems}} 条记录
                    </div>
                </div>
            `;
            
            if (totalPages > 1) {{
                paginationHTML += `
                    <div class="pagination-container">
                        <button class="pagination-btn" onclick="goToPage('${{tableId}}', 1)" ${{currentPage === 1 ? 'disabled' : ''}}>
                            首页
                        </button>
                        <button class="pagination-btn" onclick="goToPage('${{tableId}}', ${{currentPage - 1}})" ${{currentPage === 1 ? 'disabled' : ''}}>
                            上一页
                        </button>
                `;
                
                // 计算显示的页码范围
                let startPage = Math.max(1, currentPage - Math.floor(paginationConfig.maxVisiblePages / 2));
                let endPage = Math.min(totalPages, startPage + paginationConfig.maxVisiblePages - 1);
                
                if (endPage - startPage + 1 < paginationConfig.maxVisiblePages) {{
                    startPage = Math.max(1, endPage - paginationConfig.maxVisiblePages + 1);
                }}
                
                // 显示页码
                for (let i = startPage; i <= endPage; i++) {{
                    paginationHTML += `
                        <button class="pagination-btn ${{i === currentPage ? 'active' : ''}}" 
                                onclick="goToPage('${{tableId}}', ${{i}})">
                            ${{i}}
                        </button>
                    `;
                }}
                
                paginationHTML += `
                        <button class="pagination-btn" onclick="goToPage('${{tableId}}', ${{currentPage + 1}})" ${{currentPage === totalPages ? 'disabled' : ''}}>
                            下一页
                        </button>
                        <button class="pagination-btn" onclick="goToPage('${{tableId}}', ${{totalPages}})" ${{currentPage === totalPages ? 'disabled' : ''}}>
                            末页
                        </button>
                        <div class="pagination-info">
                            跳转到 <input type="number" class="pagination-input" min="1" max="${{totalPages}}" 
                                         value="${{currentPage}}" onchange="goToPage('${{tableId}}', parseInt(this.value))"> 页
                        </div>
                    </div>
                `;
            }}
            
            return paginationHTML;
        }}
        
        // 分页控制函数
        function goToPage(tableId, page) {{
            const type = tableId.replace('-table', '');
            if (type === 'weekly-compare') {{
                paginationState.weeklyCompare.currentPage = Math.max(1, Math.min(page, paginationState.weeklyCompare.totalPages));
                renderTableWithPagination(tableId, statisticsData.weekly_weekday_weekend || {{}}, 'weekly_weekday_weekend');
            }} else if (type === 'z-score') {{
                paginationState.zScore.currentPage = Math.max(1, Math.min(page, paginationState.zScore.totalPages));
                renderAnomalyTableWithPagination(tableId, anomalyData?.z_score_anomalies || [], 'z-score');
            }} else if (type === 'iqr') {{
                paginationState.iqr.currentPage = Math.max(1, Math.min(page, paginationState.iqr.totalPages));
                renderAnomalyTableWithPagination(tableId, anomalyData?.iqr_anomalies || [], 'iqr');
            }} else {{
                paginationState[type].currentPage = Math.max(1, Math.min(page, paginationState[type].totalPages));
                renderTableWithPagination(tableId, statisticsData[type] || {{}}, type);
            }}
        }}
        
        function changePageSize(tableId, newSize) {{
            paginationConfig.pageSize = parseInt(newSize);
            const type = tableId.replace('-table', '');
            if (type === 'weekly-compare') {{
                paginationState.weeklyCompare.currentPage = 1;
                renderTableWithPagination(tableId, statisticsData.weekly_weekday_weekend || {{}}, 'weekly_weekday_weekend');
            }} else if (type === 'z-score') {{
                paginationState.zScore.currentPage = 1;
                renderAnomalyTableWithPagination(tableId, anomalyData?.z_score_anomalies || [], 'z-score');
            }} else if (type === 'iqr') {{
                paginationState.iqr.currentPage = 1;
                renderAnomalyTableWithPagination(tableId, anomalyData?.iqr_anomalies || [], 'iqr');
            }} else {{
                paginationState[type].currentPage = 1;
                renderTableWithPagination(tableId, statisticsData[type] || {{}}, type);
            }}
        }}
        
        // 显示指定标签页
        function showTab(tabName) {{
            // 隐藏所有标签页内容
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 移除所有标签页的active类
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 重新渲染对应的图表
            if (tabName === 'daily') {{
                renderDailyChart();
            }} else if (tabName === 'weekly') {{
                renderWeeklyChart();
            }} else if (tabName === 'monthly') {{
                renderMonthlyChart();
            }} else if (tabName === 'weeklyCompare') {{
                renderWeeklyCompareCountChart();
                renderWeeklyCompareMeanChart();
                renderWeeklyCompareTable();
            }} else if (tabName === 'anomaly') {{
                if (anomalyData) {{
                    renderAnomalyCharts();
                    renderAnomalySummary();
                    renderAnomalyTableWithPagination('z-score-table', anomalyData?.z_score_anomalies || [], 'z-score');
                }} else {{
                    // 如果异常数据还未加载，显示加载提示
                    document.getElementById('anomaly-summary').innerHTML = '<div class="table-title">正在加载异常数据...</div>';
                }}
            }}
        }}
        

        

        
        // 渲染每日统计图表
        function renderDailyChart() {{
            const ctx = document.getElementById('dailyChart').getContext('2d');
            const dailyData = statisticsData.daily || {{}};
            const dates = Object.keys(dailyData).sort();
            const counts = dates.map(date => dailyData[date].count);
            const means = dates.map(date => dailyData[date].mean);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [
                        {{
                            label: '称重次数',
                            data: counts,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            yAxisID: 'y',
                            tension: 0.4
                        }},
                        {{
                            label: '重量均值(kg)',
                            data: means,
                            borderColor: '#f093fb',
                            backgroundColor: 'rgba(240, 147, 251, 0.1)',
                            yAxisID: 'y1',
                            tension: 0.4
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '日期'
                            }},
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 0
                            }}
                        }},
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{
                                display: true,
                                text: '称重次数'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: '重量均值(kg)'
                            }},
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每日称重次数与重量均值趋势'
                        }}
                    }}
                }}
            }});
            
            // 渲染表格
            renderTable('daily-table', dailyData, 'daily');
        }}
        
        // 渲染每周统计图表
        function renderWeeklyChart() {{
            const ctx = document.getElementById('weeklyChart').getContext('2d');
            const weeklyData = statisticsData.weekly || {{}};
            const weeks = Object.keys(weeklyData).sort();
            const counts = weeks.map(week => weeklyData[week].count);
            const means = weeks.map(week => weeklyData[week].mean);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: weeks,
                    datasets: [
                        {{
                            label: '称重次数',
                            data: counts,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            yAxisID: 'y',
                            tension: 0.4
                        }},
                        {{
                            label: '重量均值(kg)',
                            data: means,
                            borderColor: '#f093fb',
                            backgroundColor: 'rgba(240, 147, 251, 0.1)',
                            yAxisID: 'y1',
                            tension: 0.4
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '周次'
                            }},
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 0
                            }}
                        }},
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{
                                display: true,
                                text: '称重次数'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: '重量均值(kg)'
                            }},
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每周称重次数与重量均值趋势'
                        }}
                    }}
                }}
            }});
            
            // 渲染表格
            renderTable('weekly-table', weeklyData, 'weekly');
        }}
        
        // 渲染每月统计图表
        function renderMonthlyChart() {{
            const ctx = document.getElementById('monthlyChart').getContext('2d');
            const monthlyData = statisticsData.monthly || {{}};
            const months = Object.keys(monthlyData).sort();
            const counts = months.map(month => monthlyData[month].count);
            const means = months.map(month => monthlyData[month].mean);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: months,
                    datasets: [
                        {{
                            label: '称重次数',
                            data: counts,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            yAxisID: 'y',
                            tension: 0.4
                        }},
                        {{
                            label: '重量均值(kg)',
                            data: means,
                            borderColor: '#f093fb',
                            backgroundColor: 'rgba(240, 147, 251, 0.1)',
                            yAxisID: 'y1',
                            tension: 0.4
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{
                                display: true,
                                text: '月份'
                            }},
                            ticks: {{
                                maxRotation: 45,
                                minRotation: 0
                            }}
                        }},
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {{
                                display: true,
                                text: '称重次数'
                            }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {{
                                display: true,
                                text: '重量均值(kg)'
                            }},
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每月称重次数与重量均值趋势'
                        }}
                    }}
                }}
            }});
            
            // 渲染表格
            renderTable('monthly-table', monthlyData, 'monthly');
        }}
        
        // 渲染周内 vs 周末 称重次数对比图表
        function renderWeeklyCompareCountChart() {{
            const ctx = document.getElementById('weeklyCompareCountChart').getContext('2d');
            const raw = statisticsData.weekly_weekday_weekend || {{}};
            
            // 聚合成每周的 weekday / weekend 两列
            const weekToParts = {{}};
            Object.keys(raw).forEach(key => {{
                const week = key.replace(/_(weekday|weekend)$/,'');
                if (!weekToParts[week]) {{
                    weekToParts[week] = {{ weekday: null, weekend: null }};
                }}
                if (key.endsWith('_weekday')) {{
                    weekToParts[week].weekday = raw[key];
                }} else if (key.endsWith('_weekend')) {{
                    weekToParts[week].weekend = raw[key];
                }}
            }});
            const weeks = Object.keys(weekToParts).sort();
            const weekdayCounts = weeks.map(w => (weekToParts[w].weekday ? weekToParts[w].weekday.count : 0));
            const weekendCounts = weeks.map(w => (weekToParts[w].weekend ? weekToParts[w].weekend.count : 0));

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: weeks,
                    datasets: [
                        {{
                            label: '周内称重次数',
                            data: weekdayCounts,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: '#667eea',
                            borderWidth: 1
                        }},
                        {{
                            label: '周末称重次数',
                            data: weekendCounts,
                            backgroundColor: 'rgba(240, 147, 251, 0.8)',
                            borderColor: '#f093fb',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{ display: true, text: '周次' }}
                        }},
                        y: {{
                            beginAtZero: true,
                            title: {{ display: true, text: '称重次数' }}
                        }}
                    }},
                    plugins: {{
                        title: {{ display: true, text: '每周 周内 vs 周末 称重次数对比' }}
                    }}
                }}
            }});
        }}
        
        // 渲染周内 vs 周末 重量均值对比图表
        function renderWeeklyCompareMeanChart() {{
            const ctx = document.getElementById('weeklyCompareMeanChart').getContext('2d');
            const raw = statisticsData.weekly_weekday_weekend || {{}};
            
            // 聚合成每周的 weekday / weekend 两列
            const weekToParts = {{}};
            Object.keys(raw).forEach(key => {{
                const week = key.replace(/_(weekday|weekend)$/,'');
                if (!weekToParts[week]) {{
                    weekToParts[week] = {{ weekday: null, weekend: null }};
                }}
                if (key.endsWith('_weekday')) {{
                    weekToParts[week].weekday = raw[key];
                }} else if (key.endsWith('_weekend')) {{
                    weekToParts[week].weekend = raw[key];
                }}
            }});
            const weeks = Object.keys(weekToParts).sort();
            const weekdayMeans = weeks.map(w => (weekToParts[w].weekday ? weekToParts[w].weekday.mean : 0));
            const weekendMeans = weeks.map(w => (weekToParts[w].weekend ? weekToParts[w].weekend.mean : 0));

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: weeks,
                    datasets: [
                        {{
                            label: '周内重量均值(kg)',
                            data: weekdayMeans,
                            backgroundColor: 'rgba(79, 172, 254, 0.8)',
                            borderColor: '#4facfe',
                            borderWidth: 1
                        }},
                        {{
                            label: '周末重量均值(kg)',
                            data: weekendMeans,
                            backgroundColor: 'rgba(0, 242, 254, 0.8)',
                            borderColor: '#00f2fe',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false,
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            title: {{ display: true, text: '周次' }}
                        }},
                        y: {{
                            beginAtZero: true,
                            title: {{ display: true, text: '重量均值(kg)' }}
                        }}
                    }},
                    plugins: {{
                        title: {{ display: true, text: '每周 周内 vs 周末 重量均值对比' }}
                    }}
                }}
            }});
        }}
        
        // 渲染周内 vs 周末 对比表格
        function renderWeeklyCompareTable() {{
            const raw = statisticsData.weekly_weekday_weekend || {{}};
            renderTable('weekly-compare-table', raw, 'weekly_weekday_weekend');
        }}
        
        // 渲染数据表格（带分页）
        function renderTableWithPagination(tableId, data, type) {{
            const tableContainer = document.getElementById(tableId);
            const sortedKeys = Object.keys(data).sort();
            const totalItems = sortedKeys.length;
            const totalPages = Math.ceil(totalItems / paginationConfig.pageSize);
            
            // 更新分页状态
            const stateType = type === 'weekly_weekday_weekend' ? 'weeklyCompare' : type;
            paginationState[stateType].totalPages = totalPages;
            const currentPage = paginationState[stateType].currentPage;
            
            // 计算当前页的数据范围
            const startIndex = (currentPage - 1) * paginationConfig.pageSize;
            const endIndex = Math.min(startIndex + paginationConfig.pageSize, totalItems);
            const currentPageKeys = sortedKeys.slice(startIndex, endIndex);
            
            // 生成分页控件HTML
            const paginationHTML = createPaginationHTML(tableId, currentPage, totalPages, totalItems);
            
            // 生成表格HTML
            let tableHTML = paginationHTML + '<div class="table-wrapper">';
            
            if (type === 'weekly_weekday_weekend') {{
                tableHTML += '<table><thead><tr>' +
                    '<th>周次</th><th>类型</th>' +
                    '<th>称重次数</th><th>重量均值(kg)</th><th>重量标准差</th><th>最小重量(kg)</th><th>最大重量(kg)</th><th>Top3商品(次数)</th>' +
                    '</tr></thead><tbody>';

                currentPageKeys.forEach(key => {{
                    const stats = data[key];
                    if (!stats) return;
                    const week = key.replace(/_(weekday|weekend)$/,'');
                    const typeLabel = key.endsWith('_weekday') ? '周内' : (key.endsWith('_weekend') ? '周末' : '-');
                    
                    // 处理Top3商品数据
                    let top3Str = '';
                    if (stats.top3_products && stats.top3_products.length > 0) {{
                        top3Str = stats.top3_products.map(item => `${{item[0]}}(${{item[1]}})`).join(', ');
                    }}
                    
                    tableHTML += `<tr>
                        <td>${{week}}</td>
                        <td>${{typeLabel}}</td>
                        <td>${{stats.count}}</td>
                        <td>${{((stats.mean ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.std_dev ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.min ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.max ?? 0)).toFixed(2)}}</td>
                        <td>${{top3Str}}</td>
                    </tr>`;
                }});

                tableHTML += '</tbody></table>';
            }} else {{
                tableHTML += '<table><thead><tr>';
                if (type === 'daily') {{
                    tableHTML += '<th>日期</th>';
                }} else if (type === 'weekly') {{
                    tableHTML += '<th>周次</th>';
                }} else {{
                    tableHTML += '<th>月份</th>';
                }}
                tableHTML += '<th>称重次数</th><th>重量均值(kg)</th><th>重量标准差</th><th>最小重量(kg)</th><th>最大重量(kg)</th><th>Top3商品(次数)</th></tr></thead><tbody>';

                currentPageKeys.forEach(key => {{
                    const stats = data[key];
                    if (!stats) return;
                    
                    // 处理Top3商品数据
                    let top3Str = '';
                    if (stats.top3_products && stats.top3_products.length > 0) {{
                        top3Str = stats.top3_products.map(item => `${{item[0]}}(${{item[1]}})`).join(', ');
                    }}
                    
                    tableHTML += `<tr>
                        <td>${{key}}</td>
                        <td>${{stats.count}}</td>
                        <td>${{((stats.mean ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.std_dev ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.min ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.max ?? 0)).toFixed(2)}}</td>
                        <td>${{top3Str}}</td>
                    </tr>`;
                }});

                tableHTML += '</tbody></table>';
            }}
            
            tableHTML += '</div>' + paginationHTML;
            tableContainer.innerHTML = tableHTML;
        }}
        
        // 渲染数据表格（兼容旧版本，无分页）
        function renderTable(tableId, data, type) {{
            renderTableWithPagination(tableId, data, type);
        }}
        
        // 计算总体统计
        function calculateSummaryStats() {{
            const dailyData = statisticsData.daily || {{}};
            const weeklyData = statisticsData.weekly || {{}};
            const monthlyData = statisticsData.monthly || {{}};
            
            let totalCount = 0;
            let totalWeight = 0;
            let totalStd = 0;
            let validDays = 0;
            
            Object.values(dailyData).forEach(stats => {{
                totalCount += stats.count;
                totalWeight += stats.mean * stats.count;
                totalStd += stats.std_dev;
                validDays++;
            }});
            
            const avgWeight = totalCount > 0 ? totalWeight / totalCount : 0;
            const avgStd = validDays > 0 ? totalStd / validDays : 0;
            
            document.getElementById('total-count').textContent = totalCount.toLocaleString();
            document.getElementById('avg-weight').textContent = avgWeight.toFixed(2) + ' kg';
            document.getElementById('avg-std').textContent = avgStd.toFixed(2) + ' kg';
            document.getElementById('total-days').textContent = validDays;
        }}
        
        // 异常分析相关函数
        function showAnomalyTab(tabName) {{
            // 隐藏所有异常标签页内容
            const anomalyTabContents = document.querySelectorAll('.anomaly-tab-content');
            anomalyTabContents.forEach(content => content.classList.remove('active'));
            
            // 移除所有异常标签页的active类
            const anomalyNavTabs = document.querySelectorAll('#anomaly .nav-tab');
            anomalyNavTabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中的异常标签页
            document.getElementById(tabName + '-anomalies').classList.add('active');
            event.target.classList.add('active');
            
            // 渲染对应的表格
            if (tabName === 'z-score') {{
                renderAnomalyTableWithPagination('z-score-table', anomalyData?.z_score_anomalies || [], 'z-score');
            }} else if (tabName === 'iqr') {{
                renderAnomalyTableWithPagination('iqr-table', anomalyData?.iqr_anomalies || [], 'iqr');
            }} else if (tabName === 'comparison') {{
                renderComparisonTable();
            }}
        }}
        
        // 渲染异常数据表格（带分页）
        function renderAnomalyTableWithPagination(tableId, anomalies, type) {{
            const tableContainer = document.getElementById(tableId);
            if (!anomalies || anomalies.length === 0) {{
                tableContainer.innerHTML = '<div class="table-title">暂无异常数据</div>';
                return;
            }}
            
            const totalItems = anomalies.length;
            const totalPages = Math.ceil(totalItems / paginationConfig.pageSize);
            
            // 更新分页状态
            paginationState[type].totalPages = totalPages;
            const currentPage = paginationState[type].currentPage;
            
            // 计算当前页的数据范围
            const startIndex = (currentPage - 1) * paginationConfig.pageSize;
            const endIndex = Math.min(startIndex + paginationConfig.pageSize, totalItems);
            const currentPageAnomalies = anomalies.slice(startIndex, endIndex);
            
            // 生成分页控件HTML
            const paginationHTML = createPaginationHTML(tableId, currentPage, totalPages, totalItems);
            
            // 生成表格HTML
            let tableHTML = paginationHTML + '<div class="table-wrapper">';
            tableHTML += '<table><thead><tr>';
            
            if (type === 'z-score') {{
                tableHTML += '<th>数据点</th><th>Z-score值</th><th>异常程度</th><th>比值</th><th>称重AD值</th><th>零点AD值</th><th>重量(kg)</th><th>商品名称</th>';
            }} else {{
                tableHTML += '<th>数据点</th><th>比值</th><th>异常状态</th><th>称重AD值</th><th>零点AD值</th><th>重量(kg)</th><th>商品名称</th>';
            }}
            
            tableHTML += '</tr></thead><tbody>';
            
            currentPageAnomalies.forEach(anomaly => {{
                const severityClass = type === 'z-score' ? 
                    (anomaly.anomaly === '轻度异常' ? 'mild' : 'severe') : 'outlier';
                
                tableHTML += '<tr>';
                tableHTML += `<td>${{anomaly.index}}</td>`;
                
                if (type === 'z-score') {{
                    tableHTML += `<td>${{anomaly.z_score.toFixed(4)}}</td>`;
                    tableHTML += `<td><span class="anomaly-severity ${{severityClass}}">${{anomaly.anomaly}}</span></td>`;
                    tableHTML += `<td>${{anomaly.ratio.toFixed(4)}}</td>`;
                }} else {{
                    tableHTML += `<td>${{anomaly.ratio.toFixed(4)}}</td>`;
                    tableHTML += `<td><span class="anomaly-severity ${{severityClass}}">${{anomaly.anomaly}}</span></td>`;
                }}
                
                tableHTML += `<td>${{anomaly.ad_value || '-'}}</td>`;
                tableHTML += `<td>${{anomaly.zero_ad_value || '-'}}</td>`;
                tableHTML += `<td>${{anomaly.weight || '-'}}</td>`;
                tableHTML += `<td>${{anomaly.product_name || '-'}}</td>`;
                tableHTML += '</tr>';
            }});
            
            tableHTML += '</tbody></table></div>' + paginationHTML;
            tableContainer.innerHTML = tableHTML;
        }}
        
        // 渲染对比分析表格
        function renderComparisonTable() {{
            const tableContainer = document.getElementById('comparison-table');
            if (!anomalyData) {{
                tableContainer.innerHTML = '<div class="table-title">暂无对比数据</div>';
                return;
            }}
            
            const comparison = anomalyData.summary.comparison;
            const zOnlyIndices = comparison.z_only_indices || [];
            const iqrOnlyIndices = comparison.iqr_only_indices || [];
            const commonIndices = comparison.common_indices || [];
            
            let tableHTML = '<div class="table-wrapper">';
            tableHTML += '<table><thead><tr><th>异常类型</th><th>数量</th><th>数据点索引</th></tr></thead><tbody>';
            
            tableHTML += `<tr><td>Z-score独有异常</td><td>${{zOnlyIndices.length}}</td><td>${{zOnlyIndices.join(', ') || '无'}}</td></tr>`;
            tableHTML += `<tr><td>IQR独有异常</td><td>${{iqrOnlyIndices.length}}</td><td>${{iqrOnlyIndices.join(', ') || '无'}}</td></tr>`;
            tableHTML += `<tr><td>两种方法共同异常</td><td>${{commonIndices.length}}</td><td>${{commonIndices.join(', ') || '无'}}</td></tr>`;
            
            tableHTML += '</tbody></table></div>';
            tableContainer.innerHTML = tableHTML;
        }}
        
        // 渲染异常分析概览
        function renderAnomalySummary() {{
            if (!anomalyData) return;
            
            const summary = anomalyData.summary;
            document.getElementById('total-records').textContent = summary.total_records.toLocaleString();
            document.getElementById('z-anomaly-rate').textContent = summary.z_score_stats.anomaly_rate.toFixed(2) + '%';
            document.getElementById('iqr-anomaly-rate').textContent = summary.iqr_stats.anomaly_rate.toFixed(2) + '%';
            document.getElementById('common-anomalies').textContent = summary.comparison.common_count;
        }}
        
        // 渲染异常分析图表
        function renderAnomalyCharts() {{
            if (!anomalyData) return;
            
            renderAnomalyComparisonChart();
            renderZScoreDistributionChart();
        }}
        
        // 渲染异常检测方法对比图表
        function renderAnomalyComparisonChart() {{
            const ctx = document.getElementById('anomalyComparisonChart').getContext('2d');
            const summary = anomalyData.summary;
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['正常数据', 'Z-score异常', 'IQR异常', '共同异常'],
                    datasets: [{{
                        data: [
                            summary.z_score_stats.normal_count,
                            summary.z_score_stats.mild_anomaly_count + summary.z_score_stats.severe_anomaly_count,
                            summary.iqr_stats.outlier_count,
                            summary.comparison.common_count
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545',
                            '#6f42c1'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: '异常检测方法对比分布'
                        }},
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // 渲染Z-score分布图表
        function renderZScoreDistributionChart() {{
            const ctx = document.getElementById('zScoreDistributionChart').getContext('2d');
            const zAnomalies = anomalyData.z_score_anomalies || [];
            
            // 按异常程度分组
            const mildAnomalies = zAnomalies.filter(a => a.anomaly === '轻度异常');
            const severeAnomalies = zAnomalies.filter(a => a.anomaly === '重度异常');
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['轻度异常', '重度异常'],
                    datasets: [{{
                        label: '异常数量',
                        data: [mildAnomalies.length, severeAnomalies.length],
                        backgroundColor: ['#ffc107', '#dc3545'],
                        borderColor: ['#e0a800', '#c82333'],
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '异常数量'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: '异常程度'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Z-score异常程度分布'
                        }}
                    }}
                }}
            }});
        }}
        
        // 动态加载异常数据
        async function loadAnomalyData() {{
            try {{
                const response = await fetch('anomaly_data.json');
                if (response.ok) {{
                    anomalyData = await response.json();
                    console.log('异常数据加载成功:', anomalyData);
                    
                    // 初始化异常分析
                    renderAnomalySummary();
                    renderAnomalyCharts();
                }} else {{
                    console.log('没有找到异常数据文件');
                }}
            }} catch (error) {{
                console.log('加载异常数据失败:', error);
            }}
        }}
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            calculateSummaryStats();
            renderDailyChart();
            renderWeeklyCompareCountChart();
            renderWeeklyCompareMeanChart();
            
            // 动态加载异常数据
            loadAnomalyData();
        }});
    </script>
</body>
</html>
"""
        
        # 保存HTML文件
        html_file_path = os.path.join(self.output_dir, 'weight_statistics_visualization.html')
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file_path
    
    def generate_visualization(self):
        """生成完整的可视化网页"""
        print("正在生成称重数据可视化网页...")
        
        try:
            # 调用csv_processor中的统计方法获取数据
            statistics_data = csv_processor.time_based_weight_statistics()
            
            if not statistics_data:
                print("错误: 无法获取统计数据")
                return None
            
            # 生成HTML页面
            html_file_path = self.generate_html_page(statistics_data)
            
            print(f"可视化网页已生成: {html_file_path}")
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'file://{html_file_path}')
                print("已在浏览器中打开可视化页面")
            except Exception as e:
                print(f"无法自动打开浏览器: {e}")
                print(f"请手动打开文件: {html_file_path}")
            
            return html_file_path
            
        except Exception as e:
            print(f"生成可视化网页时出错: {e}")
            return None


def main():
    """主函数"""
    print("="*80)
    print("称重数据可视化网页生成器")
    print("="*80)
    
    generator = WebVisualizationGenerator()
    html_file = generator.generate_visualization()
    
    if html_file:
        print(f"\n✅ 可视化网页生成成功!")
        print(f"📁 文件位置: {html_file}")
        print(f"🌐 请在浏览器中查看结果")
    else:
        print("\n❌ 可视化网页生成失败")


if __name__ == '__main__':
    main()
