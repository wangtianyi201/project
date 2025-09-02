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
    
    def generate_html_page(self, statistics_data, anomaly_data=None, weight_time_anomaly_data=None):
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
        
        /* 无数据提示样式 */
        .no-data {{
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 1.1em;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin: 20px 0;
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
                    <button class="nav-tab" onclick="showTab('anomaly')">🚨 失准异常分析</button>
                    <button class="nav-tab" onclick="showTab('weightTimeAnomaly')">⚠️ 行为异常分析</button>
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
                        <div class="chart-title">📊 周内 vs 周末 日均称重次数对比</div>
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
                    <div class="table-title">🚨 称重数据失准异常分析</div>
                    
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
                            <h4>轻度异常数</h4>
                            <div class="summary-value" id="mild-anomalies">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>重度异常数</h4>
                            <div class="summary-value" id="severe-anomalies">-</div>
                        </div>
                    </div>
                    
                    <!-- 异常分析图表 -->
                    <div class="chart-container">
                        <div class="chart-title">📊 Z-score异常分布</div>
                        <div class="chart-wrapper">
                            <canvas id="zScoreDistributionChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 异常数据详情表格 -->
                    <div class="data-table">
                        <div class="table-title">📋 Z-score异常数据详情列表</div>
                        <div id="anomaly-table"></div>
                    </div>

                </div>
                
                <div id="weightTimeAnomaly" class="tab-content">
                    <div class="table-title">⚠️ 重量和时间异常分析</div>
                    
                    <!-- 异常分析概览 -->
                    <div class="summary-stats" id="weight-time-anomaly-summary">
                        <div class="summary-card">
                            <h4>总记录数</h4>
                            <div class="summary-value" id="total-records-wt">-</div>
            </div>
                        <div class="summary-card">
                            <h4>重量异常数</h4>
                            <div class="summary-value" id="weight-anomaly-count">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>时间异常数</h4>
                            <div class="summary-value" id="time-anomaly-count">-</div>
                        </div>
                        <div class="summary-card">
                            <h4>重量异常率</h4>
                            <div class="summary-value" id="weight-anomaly-rate">-</div>
                        </div>
                    </div>
                    
                    <!-- 异常分析图表 -->
                    <div class="chart-container">
                        <div class="chart-title">📊 异常类型分布</div>
                        <div class="chart-wrapper">
                            <canvas id="anomalyTypeChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- 重量异常数据详情表格 -->
                    <div class="data-table">
                        <div class="table-title">📋 重量异常数据详情列表</div>
                        <div id="weight-anomaly-table"></div>
                    </div>
                    
                    <!-- 时间异常数据详情表格 -->
                    <div class="data-table">
                        <div class="table-title">📋 时间异常数据详情列表</div>
                        <div id="time-anomaly-table"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 数据变量
        let statisticsData = {json.dumps(statistics_data, ensure_ascii=False, default=str)};
        let anomalyData = {json.dumps(anomaly_data, ensure_ascii=False, default=str) if anomaly_data else 'null'};
        let weightTimeAnomalyData = {json.dumps(weight_time_anomaly_data, ensure_ascii=False, default=str) if weight_time_anomaly_data else 'null'};
        
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
            anomaly: {{ currentPage: 1, totalPages: 1 }},
            weightTimeAnomaly: {{ currentPage: 1, totalPages: 1 }},
            weightAnomaly: {{ currentPage: 1, totalPages: 1 }},
            timeAnomaly: {{ currentPage: 1, totalPages: 1 }}
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
            }} else if (type === 'anomaly') {{
                paginationState.anomaly.currentPage = Math.max(1, Math.min(page, paginationState.anomaly.totalPages));
                renderAnomalyTableWithPagination(tableId, anomalyData ? anomalyData.z_score_anomalies : [], 'anomaly');
            }} else if (type === 'weight-anomaly') {{
                paginationState.weightAnomaly.currentPage = Math.max(1, Math.min(page, paginationState.weightAnomaly.totalPages));
                renderWeightTimeAnomalyTableWithPagination(tableId, weightTimeAnomalyData ? weightTimeAnomalyData.weight_anomalies : [], 'weight-anomaly');
            }} else if (type === 'time-anomaly') {{
                paginationState.timeAnomaly.currentPage = Math.max(1, Math.min(page, paginationState.timeAnomaly.totalPages));
                renderWeightTimeAnomalyTableWithPagination(tableId, weightTimeAnomalyData ? weightTimeAnomalyData.time_anomalies : [], 'time-anomaly');
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
            }} else if (type === 'anomaly') {{
                paginationState.anomaly.currentPage = 1;
                renderAnomalyTableWithPagination(tableId, anomalyData ? anomalyData.z_score_anomalies : [], 'anomaly');
            }} else if (type === 'weight-anomaly') {{
                paginationState.weightAnomaly.currentPage = 1;
                renderWeightTimeAnomalyTableWithPagination(tableId, weightTimeAnomalyData ? weightTimeAnomalyData.weight_anomalies : [], 'weight-anomaly');
            }} else if (type === 'time-anomaly') {{
                paginationState.timeAnomaly.currentPage = 1;
                renderWeightTimeAnomalyTableWithPagination(tableId, weightTimeAnomalyData ? weightTimeAnomalyData.time_anomalies : [], 'time-anomaly');
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
                    renderAnomalyTableWithPagination('anomaly-table', anomalyData.z_score_anomalies || [], 'anomaly');
                    renderAnomalyCharts();
                    renderAnomalySummary();
                }} else {{
                    // 如果异常数据还未加载，显示加载提示
                    document.getElementById('anomaly-summary').innerHTML = '<div class="table-title">正在加载异常数据...</div>';
                }}
            }} else if (tabName === 'weightTimeAnomaly') {{
                if (weightTimeAnomalyData) {{
                    renderWeightTimeAnomalyTableWithPagination('weight-anomaly-table', weightTimeAnomalyData.weight_anomalies || [], 'weight-anomaly');
                    renderWeightTimeAnomalyTableWithPagination('time-anomaly-table', weightTimeAnomalyData.time_anomalies || [], 'time-anomaly');
                    renderWeightTimeAnomalySummary();
                    renderAnomalyTypeChart();
                }} else {{
                    // 如果异常数据还未加载，显示加载提示
                    document.getElementById('weight-time-anomaly-summary').innerHTML = '<div class="table-title">正在加载重量时间异常数据...</div>';
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
            // 计算日均称重次数：周内除以5天，周末除以2天
            const weekdayCounts = weeks.map(w => {{
                const weekdayData = weekToParts[w].weekday;
                return weekdayData ? (weekdayData.count / 5) : 0;
            }});
            const weekendCounts = weeks.map(w => {{
                const weekendData = weekToParts[w].weekend;
                return weekendData ? (weekendData.count / 2) : 0;
            }});

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: weeks,
                    datasets: [
                        {{
                            label: '周内日均称重次数',
                            data: weekdayCounts,
                            backgroundColor: 'rgba(102, 126, 234, 0.8)',
                            borderColor: '#667eea',
                            borderWidth: 1
                        }},
                        {{
                            label: '周末日均称重次数',
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
                            title: {{ display: true, text: '日均称重次数' }}
                        }}
                    }},
                    plugins: {{
                        title: {{ display: true, text: '每周 周内 vs 周末 日均称重次数对比' }}
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
                    '<th>日均称重次数</th><th>重量均值(kg)</th><th>重量标准差</th><th>最小重量(kg)</th><th>最大重量(kg)</th><th>Top3商品(次数)</th>' +
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
                    
                    // 计算日均称重次数：周内除以5天，周末除以2天
                    const dailyCount = key.endsWith('_weekday') ? (stats.count / 5) : (key.endsWith('_weekend') ? (stats.count / 2) : stats.count);
                    
                    tableHTML += `<tr>
                        <td>${{week}}</td>
                        <td>${{typeLabel}}</td>
                        <td>${{dailyCount.toFixed(1)}}</td>
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
        
        // 渲染异常数据表格（带分页）
        function renderAnomalyTableWithPagination(tableId, anomalies, type) {{
            const tableContainer = document.getElementById(tableId);
            if (!anomalies || anomalies.length === 0) {{
                tableContainer.innerHTML = '<div class="no-data">暂无异常数据</div>';
                return;
            }}
            
            const totalItems = anomalies.length;
            const totalPages = Math.ceil(totalItems / paginationConfig.pageSize);
            
            // 更新分页状态
            paginationState.anomaly.totalPages = totalPages;
            const currentPage = paginationState.anomaly.currentPage;
            
            // 计算当前页的数据范围
            const startIndex = (currentPage - 1) * paginationConfig.pageSize;
            const endIndex = Math.min(startIndex + paginationConfig.pageSize, totalItems);
            const currentPageAnomalies = anomalies.slice(startIndex, endIndex);
            
            // 生成分页控件HTML
            const paginationHTML = createPaginationHTML(tableId, currentPage, totalPages, totalItems);
            
            // 生成表格HTML
            let tableHTML = paginationHTML + '<div class="table-wrapper">';
            tableHTML += '<table><thead><tr>' +
                '<th>序号</th><th>Z-score值</th><th>异常程度</th><th>比值</th>' +
                '<th>AD值</th><th>零点AD值</th><th>重量(kg)</th><th>商品名称</th>' +
                '</tr></thead><tbody>';

            currentPageAnomalies.forEach((anomaly, index) => {{
                const globalIndex = startIndex + index + 1;
                const severityClass = anomaly.anomaly === '重度异常' ? 'severe' : 
                                    anomaly.anomaly === '轻度异常' ? 'mild' : 'normal';
                
                tableHTML += `<tr>
                    <td>${{globalIndex}}</td>
                    <td>${{anomaly.z_score.toFixed(3)}}</td>
                    <td><span class="anomaly-severity ${{severityClass}}">${{anomaly.anomaly}}</span></td>
                    <td>${{anomaly.ratio.toFixed(4)}}</td>
                    <td>${{anomaly.ad_value || '-'}}</td>
                    <td>${{anomaly.zero_ad_value || '-'}}</td>
                    <td>${{anomaly.weight || '-'}}</td>
                    <td>${{anomaly.product_name || '-'}}</td>
                </tr>`;
            }});

            tableHTML += '</tbody></table></div>' + paginationHTML;
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
        
        // 异常分析相关函数（已简化，只保留Z-score）
        

        

        
        // 渲染异常分析概览
        function renderAnomalySummary() {{
            if (!anomalyData) return;
            
            const summary = anomalyData.summary;
            document.getElementById('total-records').textContent = summary.total_records.toLocaleString();
            document.getElementById('z-anomaly-rate').textContent = summary.z_score_stats.anomaly_rate.toFixed(2) + '%';
            document.getElementById('mild-anomalies').textContent = summary.z_score_stats.mild_anomaly_count.toLocaleString();
            document.getElementById('severe-anomalies').textContent = summary.z_score_stats.severe_anomaly_count.toLocaleString();
        }}
        
        // 渲染异常分析图表
        function renderAnomalyCharts() {{
            if (!anomalyData) return;
            
            renderZScoreDistributionChart();
        }}
        
        // 渲染Z-score分布图表
        function renderZScoreDistributionChart() {{
            const ctx = document.getElementById('zScoreDistributionChart').getContext('2d');
            const summary = anomalyData.summary;
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['正常数据', '轻度异常', '重度异常'],
                    datasets: [{{
                        data: [
                            summary.z_score_stats.normal_count,
                            summary.z_score_stats.mild_anomaly_count,
                            summary.z_score_stats.severe_anomaly_count
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545'
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
                            text: 'Z-score异常程度分布'
                        }},
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // 渲染重量时间异常分析概览
        function renderWeightTimeAnomalySummary() {{
            if (!weightTimeAnomalyData) return;
            
            const summary = weightTimeAnomalyData.summary;
            document.getElementById('total-records-wt').textContent = summary.total_records.toLocaleString();
            document.getElementById('weight-anomaly-count').textContent = summary.weight_anomaly_count.toLocaleString();
            document.getElementById('time-anomaly-count').textContent = summary.time_anomaly_count.toLocaleString();
            document.getElementById('weight-anomaly-rate').textContent = summary.weight_anomaly_rate.toFixed(2) + '%';
        }}
        
        // 渲染异常类型分布图表
        function renderAnomalyTypeChart() {{
            const ctx = document.getElementById('anomalyTypeChart').getContext('2d');
            const summary = weightTimeAnomalyData.summary;
            
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: ['正常数据', '重量异常', '时间异常'],
                    datasets: [{{
                        data: [
                            summary.total_records - summary.weight_anomaly_count - summary.time_anomaly_count,
                            summary.weight_anomaly_count,
                            summary.time_anomaly_count
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#dc3545'
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
                            text: '异常类型分布'
                        }},
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // 渲染重量时间异常数据表格（带分页）
        function renderWeightTimeAnomalyTableWithPagination(tableId, anomalies, type) {{
            const tableContainer = document.getElementById(tableId);
            if (!anomalies || anomalies.length === 0) {{
                tableContainer.innerHTML = '<div class="no-data">暂无异常数据</div>';
                return;
            }}
            
            const totalItems = anomalies.length;
            const totalPages = Math.ceil(totalItems / paginationConfig.pageSize);
            
            // 更新分页状态
            const stateType = type === 'weight-anomaly' ? 'weightAnomaly' : 'timeAnomaly';
            paginationState[stateType].totalPages = totalPages;
            const currentPage = paginationState[stateType].currentPage;
            
            // 计算当前页的数据范围
            const startIndex = (currentPage - 1) * paginationConfig.pageSize;
            const endIndex = Math.min(startIndex + paginationConfig.pageSize, totalItems);
            const currentPageAnomalies = anomalies.slice(startIndex, endIndex);
            
            // 生成分页控件HTML
            const paginationHTML = createPaginationHTML(tableId, currentPage, totalPages, totalItems);
            
            // 生成表格HTML
            let tableHTML = paginationHTML + '<div class="table-wrapper">';
            
            if (type === 'weight-anomaly') {{
                tableHTML += '<table><thead><tr>' +
                    '<th>序号</th><th>重量(kg)</th><th>商品名称</th><th>订单时间</th><th>创建时间</th><th>异常描述</th>' +
                    '</tr></thead><tbody>';

                currentPageAnomalies.forEach((anomaly, index) => {{
                    const globalIndex = startIndex + index + 1;
                    tableHTML += `<tr>
                        <td>${{globalIndex}}</td>
                        <td>${{anomaly.weight.toFixed(2)}}</td>
                        <td>${{anomaly.product_name || '-'}}</td>
                        <td>${{anomaly.order_time || '-'}}</td>
                        <td>${{anomaly.create_time || '-'}}</td>
                        <td><span class="anomaly-severity severe">${{anomaly.anomaly_description}}</span></td>
                    </tr>`;
                }});
            }} else if (type === 'time-anomaly') {{
                tableHTML += '<table><thead><tr>' +
                    '<th>序号</th><th>重量(kg)</th><th>商品名称</th><th>订单时间</th><th>创建时间</th><th>时间差(分钟)</th><th>异常描述</th>' +
                    '</tr></thead><tbody>';

                currentPageAnomalies.forEach((anomaly, index) => {{
                    const globalIndex = startIndex + index + 1;
                    tableHTML += `<tr>
                        <td>${{globalIndex}}</td>
                        <td>${{anomaly.weight.toFixed(2)}}</td>
                        <td>${{anomaly.product_name || '-'}}</td>
                        <td>${{anomaly.order_time || '-'}}</td>
                        <td>${{anomaly.create_time || '-'}}</td>
                        <td>${{anomaly.time_diff_minutes.toFixed(1)}}</td>
                        <td><span class="anomaly-severity severe">${{anomaly.anomaly_description}}</span></td>
                    </tr>`;
                }});
            }}

            tableHTML += '</tbody></table></div>' + paginationHTML;
            tableContainer.innerHTML = tableHTML;
        }}
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            calculateSummaryStats();
            renderDailyChart();
            renderWeeklyCompareCountChart();
            renderWeeklyCompareMeanChart();
            
            // 初始化异常分析（数据已嵌入页面）
            if (anomalyData) {{
                renderAnomalySummary();
                renderAnomalyCharts();
            }}
            
            // 初始化重量时间异常分析（数据已嵌入页面）
            if (weightTimeAnomalyData) {{
                renderWeightTimeAnomalySummary();
                renderAnomalyTypeChart();
            }}
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
            
            # 获取异常分析数据
            print("正在分析异常数据...")
            anomaly_data = csv_processor.single_scale_example_usage()
            
            # 获取重量和时间异常数据
            print("正在分析重量和时间异常数据...")
            weight_time_anomaly_data = csv_processor.detect_weight_and_time_anomalies()
            
            # 生成HTML页面
            html_file_path = self.generate_html_page(statistics_data, anomaly_data, weight_time_anomaly_data)
            
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
