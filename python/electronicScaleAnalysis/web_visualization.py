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
            
            <!-- 图表展示区域 -->
            <div class="chart-container">
                <div class="chart-title">📊 数据趋势图表</div>
                <div class="chart-wrapper">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
            
            
            
            <!-- 详细数据表格 -->
            <div class="data-table">
                <div class="nav-tabs">
                    <button class="nav-tab active" onclick="showTab('daily')">📅 每日统计</button>
                    <button class="nav-tab" onclick="showTab('weekly')">📆 每周统计</button>
                    <button class="nav-tab" onclick="showTab('monthly')">🗓️ 每月统计</button>
                    <button class="nav-tab" onclick="showTab('weeklyCompare')">⚖️ 周内 vs 周末</button>
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
                    <div class="chart-wrapper">
                        <canvas id="weeklyCompareChart"></canvas>
                    </div>
                    <div id="weekly-compare-table"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 数据变量
        let statisticsData = {json.dumps(statistics_data, ensure_ascii=False, default=str)};
        
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
                renderWeeklyCompareChart();
            }}
        }}
        
        // 渲染总体趋势图表
        function renderTrendChart() {{
            const ctx = document.getElementById('trendChart').getContext('2d');
            
            // 准备数据
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
        }}
        

        
        // 渲染每日统计图表
        function renderDailyChart() {{
            const ctx = document.getElementById('dailyChart').getContext('2d');
            const dailyData = statisticsData.daily || {{}};
            const dates = Object.keys(dailyData).sort();
            const stdDevs = dates.map(date => dailyData[date].std_dev);
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: dates,
                    datasets: [{{
                        label: '重量标准差',
                        data: stdDevs,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
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
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '重量标准差(kg)'
                            }},
                            ticks: {{
                                stepSize: 0.1,
                                maxTicksLimit: 10
                            }},
                            grid: {{
                                color: 'rgba(0,0,0,0.1)'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每日重量标准差分布'
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
            
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: weeks,
                    datasets: [{{
                        label: '称重次数',
                        data: counts,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
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
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: '称重次数'
                            }},
                            ticks: {{
                                stepSize: 500,
                                maxTicksLimit: 10
                            }},
                            grid: {{
                                color: 'rgba(0,0,0,0.1)'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每周称重次数分布'
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
            const means = months.map(month => monthlyData[month].mean);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: months,
                    datasets: [{{
                        label: '重量均值',
                        data: means,
                        borderColor: '#4facfe',
                        backgroundColor: 'rgba(79, 172, 254, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
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
                            title: {{
                                display: true,
                                text: '重量均值(kg)'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: '每月重量均值趋势'
                        }}
                    }}
                }}
            }});
            
            // 渲染表格
            renderTable('monthly-table', monthlyData, 'monthly');
        }}
        
        // 渲染周内 vs 周末 对比图表
        function renderWeeklyCompareChart() {{
            const ctx = document.getElementById('weeklyCompareChart').getContext('2d');
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
                            backgroundColor: 'rgba(102, 126, 234, 0.7)',
                            borderColor: '#667eea',
                            borderWidth: 1
                        }},
                        {{
                            label: '周末称重次数',
                            data: weekendCounts,
                            backgroundColor: 'rgba(240, 147, 251, 0.7)',
                            borderColor: '#f093fb',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
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

            // 渲染对比表格
            renderTable('weekly-compare-table', raw, 'weekly_weekday_weekend');
        }}
        
        // 渲染数据表格
        function renderTable(tableId, data, type) {{
            const tableContainer = document.getElementById(tableId);
            const sortedKeys = Object.keys(data).sort();
            
            if (type === 'weekly_weekday_weekend') {{
                let tableHTML = '<table><thead><tr>' +
                    '<th>周次</th><th>类型</th>' +
                    '<th>称重次数</th><th>重量均值(kg)</th><th>重量标准差</th><th>最小重量(kg)</th><th>最大重量(kg)</th>' +
                    '</tr></thead><tbody>';

                sortedKeys.forEach(key => {{
                    const stats = data[key];
                    if (!stats) return;
                    const week = key.replace(/_(weekday|weekend)$/,'');
                    const typeLabel = key.endsWith('_weekday') ? '周内' : (key.endsWith('_weekend') ? '周末' : '-');
                    tableHTML += `<tr>
                        <td>${{week}}</td>
                        <td>${{typeLabel}}</td>
                        <td>${{stats.count}}</td>
                        <td>${{((stats.mean ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.std_dev ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.min ?? 0)).toFixed(2)}}</td>
                        <td>${{((stats.max ?? 0)).toFixed(2)}}</td>
                    </tr>`;
                }});

                tableHTML += '</tbody></table>';
                tableContainer.innerHTML = tableHTML;
                return;
            }}

            let tableHTML = '<table><thead><tr>';
            if (type === 'daily') {{
                tableHTML += '<th>日期</th>';
            }} else if (type === 'weekly') {{
                tableHTML += '<th>周次</th>';
            }} else {{
                tableHTML += '<th>月份</th>';
            }}
            tableHTML += '<th>称重次数</th><th>重量均值(kg)</th><th>重量标准差</th><th>最小重量(kg)</th><th>最大重量(kg)</th></tr></thead><tbody>';

            sortedKeys.forEach(key => {{
                const stats = data[key];
                if (!stats) return;
                tableHTML += `<tr>
                    <td>${{key}}</td>
                    <td>${{stats.count}}</td>
                    <td>${{((stats.mean ?? 0)).toFixed(2)}}</td>
                    <td>${{((stats.std_dev ?? 0)).toFixed(2)}}</td>
                    <td>${{((stats.min ?? 0)).toFixed(2)}}</td>
                    <td>${{((stats.max ?? 0)).toFixed(2)}}</td>
                </tr>`;
            }});

            tableHTML += '</tbody></table>';
            tableContainer.innerHTML = tableHTML;
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
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {{
            calculateSummaryStats();
            renderTrendChart();
            renderDailyChart();
            renderWeeklyCompareChart();
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
