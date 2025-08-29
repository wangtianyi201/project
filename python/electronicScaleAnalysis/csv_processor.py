import csv
import os
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy import stats
import numpy as np

# 设置matplotlib支持中文显示 - 使用Windows系统常见中文字体
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "sans-serif"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def calculate_z_scores(test_ratios, reference_ratios, test_data=None):
    """计算测试数据比值相对于参考数据比值的Z-score，并判断异常程度

    Args:
        test_ratios (list): 测试数据的比值列表
        reference_ratios (list): 参考数据的比值列表
        test_data (list, optional): 测试数据的完整数据行列表

    Returns:
        list: 包含Z-score值、异常程度和原始数据的字典列表
    """
    if not reference_ratios or len(reference_ratios) < 2:
        print("警告: 参考数据不足，无法计算Z-score")
        return []

    # 计算参考数据的均值和标准差
    ref_mean = statistics.mean(reference_ratios)
    ref_std = statistics.stdev(reference_ratios)

    if ref_std == 0:
        print("警告: 参考数据的标准差为0，无法计算Z-score")
        return []

    # 计算每个测试数据的Z-score并判断异常程度
    z_score_results = []
    for i, ratio in enumerate(test_ratios):
        z_score = (ratio - ref_mean) / ref_std
        abs_z = abs(z_score)
        if abs_z > 3:
            anomaly = "重度异常"
        elif abs_z > 2:
            anomaly = "轻度异常"
        else:
            anomaly = "正常"
        
        result = {
            'z_score': z_score,
            'anomaly': anomaly,
            'ratio': ratio
        }
        
        # 如果提供了测试数据，添加原始数据行
        if test_data and i < len(test_data):
            result['original_data'] = test_data[i]
            
        z_score_results.append(result)

    return z_score_results


def check_outliers(test_ratios, lower_bound, upper_bound):
    """检查测试数据比值是否超出异常值范围

    Args:
        test_ratios (list): 测试数据的比值列表
        lower_bound (float): 异常值下限
        upper_bound (float): 异常值上限

    Returns:
        list: 包含比值和是否异常的字典列表
    """
    if not test_ratios:
        print("警告: 没有测试数据可供分析")
        return []

    outlier_results = []
    for ratio in test_ratios:
        if ratio < lower_bound or ratio > upper_bound:
            is_outlier = True
            if ratio < lower_bound:
                anomaly = f"异常 (低于下限{lower_bound:.4f})"
            else:
                anomaly = f"异常 (高于上限{upper_bound:.4f})"
        else:
            is_outlier = False
            anomaly = "正常"
        outlier_results.append({
            'ratio': ratio,
            'is_outlier': is_outlier,
            'anomaly': anomaly
        })

    return outlier_results

def detect_outliers_with_iqr(device_ratios, test_ratios, test_data=None):
    """使用四分位法检测测试数据中的异常值

    Args:
        device_ratios (list): 设备数据的比值列表（用于计算四分位）
        test_ratios (list): 测试数据的比值列表（需要检查是否异常）
        test_data (list, optional): 测试数据的完整数据行列表

    Returns:
        list: 包含比值、是否异常和原始数据的字典列表
    """
    if not device_ratios or len(device_ratios) < 2:
        print("警告: 设备数据不足，无法计算四分位")
        return []
    
    # 计算四分位
    q1 = np.percentile(device_ratios, 25)
    q3 = np.percentile(device_ratios, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # 打印四分位计算结果
    print(f"Q1: {q1:.4f}, Q3: {q3:.4f}, IQR: {iqr:.4f}")
    print(f"异常值范围: [{lower_bound:.4f}, {upper_bound:.4f}]")
    
    # 检查测试数据中的异常值
    outlier_results = check_outliers(test_ratios, lower_bound, upper_bound)
    
    # 如果提供了测试数据，添加原始数据行
    if test_data:
        for i, result in enumerate(outlier_results):
            if i < len(test_data):
                result['original_data'] = test_data[i]
                
    return outlier_results


def analyze_file_and_get_ratios(file_path, ad_column='称重AD值', zero_ad_column='零点AD值', weight_column='重量(kg)'):
    """分析文件并获取比值列表和完整数据

    Args:
        file_path (str): 文件路径
        ad_column (str): 称重AD值列名
        zero_ad_column (str): 零点AD值列名
        weight_column (str): 重量值列名

    Returns:
        tuple: (比值列表, 完整数据行列表)
    """
    processor = CSVProcessor()

    try:
        data = processor.read_csv(file_path)
        print(f"成功读取 {file_path} 中的 {len(data)} 条记录")
    except FileNotFoundError as e:
        print(e)
        return [], []

    valid_ratios = []
    valid_data = []

    for row in data:
        try:
            ad_value = float(row[ad_column])
            zero_ad_value = float(row[zero_ad_column])
            weight_value = float(row[weight_column])

            k_value = ad_value - zero_ad_value
            ratio = k_value / weight_value / 1000 if weight_value != 0 else 0

            valid_ratios.append(ratio)
            valid_data.append(row)  # 保存完整数据行
        except (ValueError, KeyError) as e:
            continue

    return valid_ratios, valid_data


class CSVProcessor:
    """CSV文件处理器，提供读取、处理和写入CSV文件的功能"""

    def read_csv(self, file_path):
        """读取CSV文件并返回数据

        Args:
            file_path (str): CSV文件路径

        Returns:
            list: 包含CSV数据的列表，每个元素是一行数据（字典形式）
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def write_csv(self, file_path, data, fieldnames=None):
        """将数据写入CSV文件

        Args:
            file_path (str): 输出文件路径
            data (list): 要写入的数据，每个元素是一行数据（字典形式）
            fieldnames (list, optional): 列名列表。如果为None，则从data的第一个元素获取
        """
        if not data:
            print("警告: 没有数据可写入")
            return

        # 如果未提供fieldnames，则从data的第一个元素获取
        if fieldnames is None:
            fieldnames = data[0].keys()

        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def filter_data(self, data, condition_func):
        """根据条件过滤数据

        Args:
            data (list): 要过滤的数据
            condition_func (function): 条件函数，返回True表示保留该行

        Returns:
            list: 过滤后的数据
        """
        return [row for row in data if condition_func(row)]

    def process_column(self, data, column_name, process_func):
        """对指定列应用处理函数

        Args:
            data (list): 要处理的数据
            column_name (str): 列名
            process_func (function): 处理函数

        Returns:
            list: 处理后的数据
        """
        for row in data:
            if column_name in row:
                row[column_name] = process_func(row[column_name])
        return data

    def aggregate_data(self, data, group_by_column, agg_column, agg_func):
        """根据指定列分组并聚合

        Args:
            data (list): 要聚合的数据
            group_by_column (str): 分组列名
            agg_column (str): 要聚合的列名
            agg_func (function): 聚合函数

        Returns:
            dict: 聚合结果
        """
        result = {}
        for row in data:
            group_key = row[group_by_column]
            if group_key not in result:
                result[group_key] = []
            if agg_column in row:
                result[group_key].append(row[agg_column])

        # 应用聚合函数
        for key in result:
            result[key] = agg_func(result[key])

        return result

    def group_by_product(self, data, product_column):
        """根据商品名称分类数据

        Args:
            data (list): 要分组的数据
            product_column (str): 商品名称列名

        Returns:
            dict: 按商品名称分组的数据
        """
        grouped_data = defaultdict(list)
        for row in data:
            product_name = row[product_column]
            grouped_data[product_name].append(row)
        return dict(grouped_data)

    def descriptive_analysis(self, data, weight_column):
        """对重量数据进行描述性分析

        Args:
            data (list): 要分析的数据
            weight_column (str): 重量数据列名

        Returns:
            dict: 包含均值、中位数、标准差等描述性统计信息
        """
        # 提取重量数据并转换为浮点数
        weights = [float(row[weight_column]) for row in data if row[weight_column]]

        if not weights:
            return {
                'count': 0,
                'mean': None,
                'median': None,
                'std_dev': None,
                'min': None,
                'max': None
            }

        # 计算描述性统计信息
        analysis = {
            'count': len(weights),
            'mean': statistics.mean(weights),
            'median': statistics.median(weights),
            'min': min(weights),
            'max': max(weights)
        }

        # 计算标准差（如果样本数大于1）
        if len(weights) > 1:
            analysis['std_dev'] = statistics.stdev(weights)
        else:
            analysis['std_dev'] = 0.0

        return analysis

    def display_all_columns(self, data, max_rows=10):
        """显示数据中的所有列

        Args:
            data (list): 要显示的数据
            max_rows (int): 最多显示的行数
        """
        if not data:
            print("没有数据可显示")
            return

        # 打印列名
        columns = data[0].keys()
        print("\n所有列名:")
        print(", ".join(columns))

        # 打印数据
        print(f"\n前{min(max_rows, len(data))}行数据:")
        for i, row in enumerate(data[:max_rows]):
            print(f"行 {i+1}:")
            for col, value in row.items():
                print(f"  {col}: {value}")
            print()



def analyze_weight_data(file_path, ad_column='称重AD值', zero_ad_column='零点AD值', weight_column='重量(kg)'):
    """分析称重数据CSV文件，计算K值和比值

    Args:
        file_path (str): CSV文件路径
        ad_column (str): 称重AD值列名
        zero_ad_column (str): 零点AD值列名
        weight_column (str): 重量值列名
    """
    processor = CSVProcessor()

    # 读取数据
    try:
        data = processor.read_csv(file_path)
        print(f"成功读取 {len(data)} 条记录")
    except FileNotFoundError as e:
        print(e)
        return

    # 计算每行数据的K值和比值
    results = []
    valid_ratios = []  # 存储有效的比值用于统计分析

    print("\n计算K值和比值:")
    print("=" * 60)

    for i, row in enumerate(data):
        try:
            # 获取必要的值
            ad_value = float(row[ad_column])
            zero_ad_value = float(row[zero_ad_column])
            weight_value = float(row[weight_column])

            # 计算K值
            k_value = ad_value - zero_ad_value

            # 计算比值
            ratio = k_value / weight_value / 1000 if weight_value != 0 else 0

            # 保存计算结果
            row['K值'] = k_value
            row['比值'] = ratio
            results.append(row)

            # 收集有效比值用于统计分析
            valid_ratios.append(ratio)

            # 显示前10行的计算结果
            if i < 10000:
                print(f"行 {i + 1}: K值={k_value:.2f}, 比值={ratio:.4f}")

        except (ValueError, KeyError) as e:
            print(f"警告: 第{i + 1}行数据有误，跳过计算: {e}")
            continue

    # 对比值进行描述性分析
    if valid_ratios:
        print(f"比值的描述性分析 (共{len(valid_ratios)}条有效记录):")
        print("=" * 40)
        print(f"均值: {statistics.mean(valid_ratios):.4f}")
        print(f"中位数: {statistics.median(valid_ratios):.4f}")
        print(f"最小值: {min(valid_ratios):.4f}")
        print(f"最大值: {max(valid_ratios):.4f}")

        if len(valid_ratios) > 1:
            print(f"标准差: {statistics.stdev(valid_ratios):.4f}")
        else:
            print("标准差: 0.0000 (样本数不足)")

        # 绘制比值折线图
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(range(1, len(valid_ratios) + 1), valid_ratios, marker='o', linestyle='-', color='blue')
        plt.title('比值变化趋势')
        plt.xlabel('数据点序号')
        plt.ylabel('比值')
        plt.grid(True)

        # 绘制比值直方图
        plt.subplot(1, 2, 2)
        plt.hist(valid_ratios, bins=20, color='green', alpha=0.7)
        plt.title('比值分布直方图')
        plt.xlabel('比值')
        plt.ylabel('频率')
        plt.grid(True)

        plt.tight_layout()
        plt.show()


"""
单台秤的称重失准异常分析
"""
def single_scale_example_usage():
    """示例用法"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义文件路径
    test_file = os.path.join(current_dir, '设备3PLBJ0700_称重数据_2025-01-01_2025-08-25.csv')
    device_file = os.path.join(current_dir, '设备3PLBJ0700_称重数据_2025-01-01_2025-08-25.csv')
    
    # 检查文件是否存在
    if not os.path.exists(test_file):
        print(f"错误: 找不到测试数据文件 '{test_file}'")
        return
    
    if not os.path.exists(device_file):
        print(f"错误: 找不到设备数据文件 '{device_file}'")
        return

    # # 对比值进行描述性分析
    # print("\n测试数据比值的描述性分析:")
    # analyze_weight_data(test_file)
    #
    # print("\n设备数据比值的描述性分析:")
    # analyze_weight_data(device_file)

    
    # 分析文件并获取比值和完整数据
    print("正在分析测试数据文件...")
    test_ratios, test_data = analyze_file_and_get_ratios(test_file)
    
    print("正在分析设备数据文件...")
    device_ratios, _ = analyze_file_and_get_ratios(device_file)  # 设备数据只需要比值
    
    # 检查是否有足够的有效比值
    if not test_ratios:
        print("错误: 测试数据中没有有效比值")
        return
    
    if len(device_ratios) < 2:
        print("错误: 设备数据中有效比值不足")
        return

    # 计算Z-score并传递原始测试数据
    z_score_results = calculate_z_scores(test_ratios, device_ratios, test_data)
    
    if z_score_results:
        print("\nZ-score计算结果:")
        print("=" * 80)
        print(f"{'数据点':<10}{'Z-score值':<15}{'异常程度':<15}")
        print("=" * 80)
        
        # 收集Z-score异常数据
        z_anomalies = []
        for i, result in enumerate(z_score_results):
            z = result['z_score']
            anomaly = result['anomaly']
            # print(f"{i+1:<10}{z:<15.4f}{anomaly:<15}")
            # 收集异常数据
            if anomaly != "正常":
                z_anomalies.append((i+1, result))
        
        # 输出Z-score异常数据行
        if z_anomalies:
            print("\nZ-score异常数据行:")
            print("=" * 120)
            # 获取所有可能的列名
            all_columns = set()
            for _, result in z_anomalies:
                if 'original_data' in result:
                    all_columns.update(result['original_data'].keys())
            
            # 确保关键列在前
            key_columns = ['称重AD值', '零点AD值', '重量(kg)']
            columns = key_columns + [col for col in all_columns if col not in key_columns]
            
            # 打印表头
            header = "数据点" + "	" + "\t".join(columns)
            print(header)
            print("=" * 120)
            
            # 打印异常数据行
            for idx, result in z_anomalies:
                if 'original_data' in result:
                    row_data = result['original_data']
                    row_values = [idx] + [row_data.get(col, "-") for col in columns]
                    print("\t".join(map(str, row_values)))

    # 使用四分位法检测测试数据中的异常值并传递原始测试数据
    outlier_results = detect_outliers_with_iqr(device_ratios, test_ratios, test_data)
    
    if outlier_results:
        print("\nIQR异常值检测结果:")
        print("=" * 80)
        print(f"{'数据点':<10}{'比值':<15}{'状态':<30}")
        print("=" * 80)
        
        # 收集IQR异常数据
        iqr_anomalies = []
        for i, result in enumerate(outlier_results):
            ratio = result['ratio']
            anomaly = result['anomaly']
            # print(f"{i+1:<10}{ratio:<15.4f}{anomaly:<30}")
            # 收集异常数据
            if 'is_outlier' in result and result['is_outlier']:
                iqr_anomalies.append((i+1, result))
            elif '异常' in anomaly:
                iqr_anomalies.append((i+1, result))
        
        # 输出IQR异常数据行
        if iqr_anomalies:
            print("\nIQR异常数据行:")
            print("=" * 120)
            # 获取所有可能的列名
            all_columns = set()
            for _, result in iqr_anomalies:
                if 'original_data' in result:
                    all_columns.update(result['original_data'].keys())
            
            # 确保关键列在前
            key_columns = ['称重AD值', '零点AD值', '重量(kg)']
            columns = key_columns + [col for col in all_columns if col not in key_columns]
            
            # 打印表头
            header = "数据点" + "	" + "\t".join(columns)
            print(header)
            print("=" * 120)
            
            # 打印异常数据行
            for idx, result in iqr_anomalies:
                if 'original_data' in result:
                    row_data = result['original_data']
                    row_values = [idx] + [row_data.get(col, "-") for col in columns]
                    print("\t".join(map(str, row_values)))
            
        # 对比两种方法检测到的异常数据行坐标
        if 'z_anomalies' in locals() and 'iqr_anomalies' in locals():
            z_anomaly_indices = set([idx for idx, _ in z_anomalies])
            iqr_anomaly_indices = set([idx for idx, _ in iqr_anomalies])
            
            print("\n两种方法检测异常数据行坐标对比:")
            print("=" * 100)
            print(f"{'比较类型':<20}{'行坐标'}")
            print("=" * 100)
            
            # 只在Z-score中检测到的异常
            z_only = z_anomaly_indices - iqr_anomaly_indices
            if z_only:
                print(f"{'Z-score独有异常':<20}{', '.join(map(str, sorted(z_only)))}")
            else:
                print(f"{'Z-score独有异常':<20}无")
            
            # 只在IQR中检测到的异常
            iqr_only = iqr_anomaly_indices - z_anomaly_indices
            if iqr_only:
                print(f"{'IQR独有异常':<20}{', '.join(map(str, sorted(iqr_only)))}")
            else:
                print(f"{'IQR独有异常':<20}无")
            
            # 两种方法都检测到的异常
            common = z_anomaly_indices & iqr_anomaly_indices
            if common:
                print(f"{'两种方法共异常':<20}{', '.join(map(str, sorted(common)))}")
            else:
                print(f"{'两种方法共异常':<20}无")
            
            print("=" * 100)


"""
按时间分组统计称重数据
"""
def time_based_weight_statistics():
    """按每日、每周、每月时间计算称重的次数，重量的均值、标准差"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义文件路径
    data_file = os.path.join(current_dir, '设备L30DG0091_称重数据_2025-05-31_2025-08-28.csv')
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"错误: 找不到数据文件 '{data_file}'")
        return
    
    # 创建CSV处理器
    processor = CSVProcessor()
    
    try:
        # 读取数据
        data = processor.read_csv(data_file)
        print(f"成功读取 {len(data)} 条记录")
    except FileNotFoundError as e:
        print(e)
        return
    
    # 检查数据是否包含必要的列
    if not data:
        print("错误: 数据文件为空")
        return
    
    # 检查必要的列是否存在（支持多种可能的列名）
    time_column = None
    weight_column = None
    product_column = None
    
    # 查找时间列（支持多种可能的名称）
    for col in data[0].keys():
        if '时间' in col or '订单时间' in col or '创建时间' in col:
            time_column = col
            break
    
    # 查找重量列
    for col in data[0].keys():
        if '重量' in col:
            weight_column = col
            break
    
    # 查找商品名称列（尽量匹配更明确的列名）
    for col in data[0].keys():
        if ('商品' in col) or ('品名' in col) or ('产品' in col) or ('菜品' in col):
            product_column = col
            break
    
    if not time_column or not weight_column:
        print(f"错误: 缺少必要的列")
        print(f"可用列: {list(data[0].keys())}")
        print(f"需要找到时间列和重量列")
        return
    
    print(f"使用时间列: {time_column}")
    print(f"使用重量列: {weight_column}")
    if product_column:
        print(f"使用商品列: {product_column}")
    
    # 数据预处理：解析时间并过滤有效数据
    processed_data = []
    for row in data:
        try:
            # 解析称重时间
            time_str = row[time_column]
            weight = float(row[weight_column])
            
            # 尝试多种时间格式
            import datetime
            parsed_time = None
            
            # 尝试常见的时间格式
            time_formats = [
                '%Y-%m-%dT%H:%M:%S',  # ISO 8601格式: 2025-08-21T07:31:40
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d'
            ]
            
            for fmt in time_formats:
                try:
                    parsed_time = datetime.datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_time is None:
                print(f"警告: 无法解析时间格式: {time_str}")
                continue
            
            # 添加解析后的时间信息
            row['parsed_time'] = parsed_time
            row['date'] = parsed_time.date()
            iso_year, iso_week, _ = parsed_time.isocalendar()
            row['iso_year'] = iso_year
            row['week'] = iso_week  # ISO周数
            row['month'] = parsed_time.month
            row['year'] = parsed_time.year
            row['weight'] = weight
            if product_column:
                row['product_name'] = (row.get(product_column) or '').strip()
            
            processed_data.append(row)
            
        except (ValueError, KeyError) as e:
            continue
    
    if not processed_data:
        print("错误: 没有有效的数据可处理")
        return
    
    print(f"成功处理 {len(processed_data)} 条有效记录")
    
    # 按时间分组统计
    daily_stats = defaultdict(list)
    weekly_stats = defaultdict(list)
    monthly_stats = defaultdict(list)
    
    # 商品名称收集（仅记录重量>0且有商品名的记录）
    from collections import Counter
    daily_product_names = defaultdict(list)
    weekly_product_names = defaultdict(list)
    monthly_product_names = defaultdict(list)
    
    for row in processed_data:
        # 按日期分组
        date_key = row['date']
        daily_stats[date_key].append(row['weight'])
        if product_column and row.get('product_name') and row['weight'] > 0:
            daily_product_names[date_key].append(row['product_name'])
        
        # 按周分组
        week_key = f"{row['iso_year']}-W{row['week']:02d}"
        weekly_stats[week_key].append(row['weight'])
        if product_column and row.get('product_name') and row['weight'] > 0:
            weekly_product_names[week_key].append(row['product_name'])
        
        # 按月分组
        month_key = f"{row['year']}-{row['month']:02d}"
        monthly_stats[month_key].append(row['weight'])
        if product_column and row.get('product_name') and row['weight'] > 0:
            monthly_product_names[month_key].append(row['product_name'])
    
    # 计算统计信息
    def calculate_statistics(weight_list):
        """计算重量列表的统计信息"""
        if not weight_list:
            return None
        
        weights = [w for w in weight_list if w > 0]  # 过滤掉零重量或负重量
        if not weights:
            return None
        
        return {
            'count': len(weights),
            'mean': statistics.mean(weights),
            'std_dev': statistics.stdev(weights) if len(weights) > 1 else 0.0,
            'min': min(weights),
            'max': max(weights)
        }
    
    # 计算每日统计
    print("\n" + "="*80)
    print("每日称重统计")
    print("="*80)
    header_daily = f"{'日期':<12}{'称重次数':<10}{'重量均值(kg)':<15}{'重量标准差':<15}{'最小重量':<12}{'最大重量':<12}"
    if product_column:
        header_daily += f"{'Top3商品(次数)':<40}"
    print(header_daily)
    print("-"*80)
    
    daily_results = {}
    for date in sorted(daily_stats.keys()):
        stats = calculate_statistics(daily_stats[date])
        if stats:
            # 将日期转换为字符串格式作为键
            date_key = date.strftime('%Y-%m-%d')
            # 计算Top3商品
            top3_str = ''
            counts = {}
            top3 = []
            if product_column:
                names = daily_product_names.get(date, [])
                if names:
                    counts = Counter(names)
                    top3 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                    top3_str = ", ".join([f"{name}({cnt})" for name, cnt in top3])
            # 保存与输出
            daily_results[date_key] = {**stats, **({ 'top3_products': top3 } if product_column else {})}
            line = f"{date_key:<12}{stats['count']:<10}{stats['mean']:<15.2f}{stats['std_dev']:<15.2f}{stats['min']:<12.2f}{stats['max']:<12.2f}"
            if product_column:
                line += f"{top3_str:<40}"
            print(line)
    
    # 计算每周统计
    print("\n" + "="*80)
    print("每周称重统计")
    print("="*80)
    header_weekly = f"{'周次':<12}{'称重次数':<10}{'重量均值(kg)':<15}{'重量标准差':<15}{'最小重量':<12}{'最大重量':<12}"
    if product_column:
        header_weekly += f"{'Top3商品(次数)':<40}"
    print(header_weekly)
    print("-"*80)
    
    weekly_results = {}
    for week in sorted(weekly_stats.keys()):
        stats = calculate_statistics(weekly_stats[week])
        if stats:
            # 计算Top3商品
            top3_str = ''
            counts = {}
            top3 = []
            if product_column:
                names = weekly_product_names.get(week, [])
                if names:
                    counts = Counter(names)
                    top3 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                    top3_str = ", ".join([f"{name}({cnt})" for name, cnt in top3])
            weekly_results[week] = {**stats, **({ 'top3_products': top3 } if product_column else {})}
            line = f"{week:<12}{stats['count']:<10}{stats['mean']:<15.2f}{stats['std_dev']:<15.2f}{stats['min']:<12.2f}{stats['max']:<12.2f}"
            if product_column:
                line += f"{top3_str:<40}"
            print(line)
    
    # 计算每周周内和周末对比统计
    print("\n" + "="*80)
    print("每周周内(工作日)和周末称重对比统计")
    print("="*80)
    
    # 按周分组周内和周末数据
    weekly_weekday_stats = defaultdict(list)
    weekly_weekend_stats = defaultdict(list)
    weekly_weekday_products = defaultdict(list)
    weekly_weekend_products = defaultdict(list)
    
    for row in processed_data:
        week_key = f"{row['iso_year']}-W{row['week']:02d}"
        # 判断是否为周末 (5=周六, 6=周日)
        is_weekend = row['parsed_time'].weekday() >= 5
        
        if is_weekend:
            weekly_weekend_stats[week_key].append(row['weight'])
            if product_column and row.get('product_name') and row['weight'] > 0:
                weekly_weekend_products[week_key].append(row['product_name'])
        else:
            weekly_weekday_stats[week_key].append(row['weight'])
            if product_column and row.get('product_name') and row['weight'] > 0:
                weekly_weekday_products[week_key].append(row['product_name'])
    
    # 输出周内和周末对比统计
    header_weekday_weekend = f"{'周次':<12}{'类型':<8}{'称重次数':<10}{'重量均值(kg)':<15}{'重量标准差':<15}{'最小重量':<12}{'最大重量':<12}"
    if product_column:
        header_weekday_weekend += f"{'Top3商品(次数)':<40}"
    print(header_weekday_weekend)
    print("-"*80)
    
    weekly_weekday_weekend_results = {}
    for week in sorted(set(list(weekly_weekday_stats.keys()) + list(weekly_weekend_stats.keys()))):
        # 周内统计
        if week in weekly_weekday_stats:
            weekday_stats = calculate_statistics(weekly_weekday_stats[week])
            if weekday_stats:
                # 计算Top3商品
                top3_str = ''
                top3 = []
                if product_column:
                    names = weekly_weekday_products.get(week, [])
                    if names:
                        counts = Counter(names)
                        top3 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                        top3_str = ", ".join([f"{name}({cnt})" for name, cnt in top3])
                
                weekly_weekday_weekend_results[f"{week}_weekday"] = {**weekday_stats, **({ 'top3_products': top3 } if product_column else {})}
                line = f"{week:<12}{'周内':<8}{weekday_stats['count']:<10}{weekday_stats['mean']:<15.2f}{weekday_stats['std_dev']:<15.2f}{weekday_stats['min']:<12.2f}{weekday_stats['max']:<12.2f}"
                if product_column:
                    line += f"{top3_str:<40}"
                print(line)
        
        # 周末统计
        if week in weekly_weekend_stats:
            weekend_stats = calculate_statistics(weekly_weekend_stats[week])
            if weekend_stats:
                # 计算Top3商品
                top3_str = ''
                top3 = []
                if product_column:
                    names = weekly_weekend_products.get(week, [])
                    if names:
                        counts = Counter(names)
                        top3 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                        top3_str = ", ".join([f"{name}({cnt})" for name, cnt in top3])
                
                weekly_weekday_weekend_results[f"{week}_weekend"] = {**weekend_stats, **({ 'top3_products': top3 } if product_column else {})}
                line = f"{week:<12}{'周末':<8}{weekend_stats['count']:<10}{weekend_stats['mean']:<15.2f}{weekend_stats['std_dev']:<15.2f}{weekend_stats['min']:<12.2f}{weekend_stats['max']:<12.2f}"
                if product_column:
                    line += f"{top3_str:<40}"
                print(line)
    
    # 计算周内和周末的总体对比统计
    print("\n" + "-"*80)
    print("周内(工作日) vs 周末 总体对比统计")
    print("-"*80)
    
    # 合并所有周内数据
    all_weekday_weights = []
    all_weekday_products = []
    for weights in weekly_weekday_stats.values():
        all_weekday_weights.extend(weights)
    for products in weekly_weekday_products.values():
        all_weekday_products.extend(products)
    
    # 合并所有周末数据
    all_weekend_weights = []
    all_weekend_products = []
    for weights in weekly_weekend_stats.values():
        all_weekend_weights.extend(weights)
    for products in weekly_weekend_products.values():
        all_weekend_products.extend(products)
    
    # 计算总体统计
    weekday_total_stats = calculate_statistics(all_weekday_weights)
    weekend_total_stats = calculate_statistics(all_weekend_weights)
    
    if weekday_total_stats and weekend_total_stats:
        print(f"{'类型':<8}{'称重次数':<10}{'重量均值(kg)':<15}{'重量标准差':<15}{'最小重量':<12}{'最大重量':<12}")
        print("-"*80)
        
        # 周内总体统计
        line = f"{'周内':<8}{weekday_total_stats['count']:<10}{weekday_total_stats['mean']:<15.2f}{weekday_total_stats['std_dev']:<15.2f}{weekday_total_stats['min']:<12.2f}{weekday_total_stats['max']:<12.2f}"
        print(line)
        
        # 周末总体统计
        line = f"{'周末':<8}{weekend_total_stats['count']:<10}{weekend_total_stats['mean']:<15.2f}{weekend_total_stats['std_dev']:<15.2f}{weekend_total_stats['min']:<12.2f}{weekend_total_stats['max']:<12.2f}"
        print(line)
        
        # 计算差异百分比
        count_diff_pct = ((weekend_total_stats['count'] - weekday_total_stats['count']) / weekday_total_stats['count'] * 100) if weekday_total_stats['count'] > 0 else 0
        mean_diff_pct = ((weekend_total_stats['mean'] - weekday_total_stats['mean']) / weekday_total_stats['mean'] * 100) if weekday_total_stats['mean'] > 0 else 0
        
        print(f"\n差异分析:")
        print(f"称重次数差异: 周末比周内 {count_diff_pct:+.1f}%")
        print(f"重量均值差异: 周末比周内 {mean_diff_pct:+.1f}%")
        
        # Top3商品对比
        if product_column:
            print(f"\nTop3商品对比:")
            if all_weekday_products:
                weekday_counts = Counter(all_weekday_products)
                weekday_top3 = sorted(weekday_counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                print(f"周内Top3: {', '.join([f'{name}({cnt})' for name, cnt in weekday_top3])}")
            
            if all_weekend_products:
                weekend_counts = Counter(all_weekend_products)
                weekend_top3 = sorted(weekend_counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                print(f"周末Top3: {', '.join([f'{name}({cnt})' for name, cnt in weekend_top3])}")
    
    # 计算每月统计
    print("\n" + "="*80)
    print("每月称重统计")
    print("="*80)
    header_monthly = f"{'月份':<12}{'称重次数':<10}{'重量均值(kg)':<15}{'重量标准差':<15}{'最小重量':<12}{'最大重量':<12}"
    if product_column:
        header_monthly += f"{'Top3商品(次数)':<40}"
    print(header_monthly)
    print("-"*80)
    
    monthly_results = {}
    for month in sorted(monthly_stats.keys()):
        stats = calculate_statistics(monthly_stats[month])
        if stats:
            # 计算Top3商品
            top3_str = ''
            counts = {}
            top3 = []
            if product_column:
                names = monthly_product_names.get(month, [])
                if names:
                    counts = Counter(names)
                    top3 = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:3]
                    top3_str = ", ".join([f"{name}({cnt})" for name, cnt in top3])
            monthly_results[month] = {**stats, **({ 'top3_products': top3 } if product_column else {})}
            line = f"{month:<12}{stats['count']:<10}{stats['mean']:<15.2f}{stats['std_dev']:<15.2f}{stats['min']:<12.2f}{stats['max']:<12.2f}"
            if product_column:
                line += f"{top3_str:<40}"
            print(line)
    
    # # 生成可视化图表
    # try:
    #     # 创建图表
    #     fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    #     fig.suptitle('称重数据时间分布统计', fontsize=16, fontweight='bold')
        
    #     # 1. 每日称重次数趋势
    #     if daily_results:
    #         dates = list(daily_results.keys())
    #         counts = [daily_results[date]['count'] for date in dates]
            
    #         axes[0, 0].plot(dates, counts, marker='o', linewidth=2, markersize=4)
    #         axes[0, 0].set_title('每日称重次数趋势')
    #         axes[0, 0].set_xlabel('日期')
    #         axes[0, 0].set_ylabel('称重次数')
    #         axes[0, 0].tick_params(axis='x', rotation=45)
    #         axes[0, 0].grid(True, alpha=0.3)
        
    #     # 2. 每日重量均值趋势
    #     if daily_results:
    #         means = [daily_results[date]['mean'] for date in dates]
            
    #         axes[0, 1].plot(dates, means, marker='s', linewidth=2, markersize=4, color='orange')
    #         axes[0, 1].set_title('每日重量均值趋势')
    #         axes[0, 1].set_xlabel('日期')
    #         axes[0, 1].set_ylabel('重量均值(kg)')
    #         axes[0, 1].tick_params(axis='x', rotation=45)
    #         axes[0, 1].grid(True, alpha=0.3)
        
    #     # 3. 每周称重次数对比
    #     if weekly_results:
    #         weeks = list(weekly_results.keys())
    #         week_counts = [weekly_results[week]['count'] for week in weeks]
            
    #         axes[1, 0].bar(weeks, week_counts, color='skyblue', alpha=0.7)
    #         axes[1, 0].set_title('每周称重次数对比')
    #         axes[1, 0].set_xlabel('周次')
    #         axes[1, 0].set_ylabel('称重次数')
    #         axes[1, 0].tick_params(axis='x', rotation=45)
    #         axes[1, 0].grid(True, alpha=0.3)
        
    #     # 4. 每月重量标准差对比
    #     if monthly_results:
    #         months = list(monthly_results.keys())
    #         month_stds = [monthly_results[month]['std_dev'] for month in months]
            
    #         axes[1, 1].bar(months, month_stds, color='lightcoral', alpha=0.7)
    #         axes[1, 1].set_title('每月重量标准差对比')
    #         axes[1, 1].set_xlabel('月份')
    #         axes[1, 1].set_ylabel('重量标准差(kg)')
    #         axes[1, 1].tick_params(axis='x', rotation=45)
    #         axes[1, 1].grid(True, alpha=0.3)
        
    #     plt.tight_layout()
    #     plt.show()
        
    # except Exception as e:
    #     print(f"生成图表时出错: {e}")
    
    # # 保存统计结果到CSV文件
    # try:
    #     # 保存每日统计
    #     daily_output_file = os.path.join(current_dir, '每日称重统计.csv')
    #     daily_csv_data = []
    #     for date, stats in daily_results.items():
    #         daily_csv_data.append({
    #             '日期': str(date),
    #             '称重次数': stats['count'],
    #             '重量均值(kg)': round(stats['mean'], 2),
    #             '重量标准差': round(stats['std_dev'], 2),
    #             '最小重量(kg)': round(stats['min'], 2),
    #             '最大重量(kg)': round(stats['max'], 2)
    #         })
        
    #     processor.write_csv(daily_output_file, daily_csv_data)
    #     print(f"\n每日统计结果已保存到: {daily_output_file}")
        
    #     # 保存每周统计
    #     weekly_output_file = os.path.join(current_dir, '每周称重统计.csv')
    #     weekly_csv_data = []
    #     for week, stats in weekly_results.items():
    #         weekly_csv_data.append({
    #             '周次': week,
    #             '称重次数': stats['count'],
    #             '重量均值(kg)': round(stats['mean'], 2),
    #             '重量标准差': round(stats['std_dev'], 2),
    #             '最小重量(kg)': round(stats['min'], 2),
    #             '最大重量(kg)': round(stats['max'], 2)
    #         })
        
    #     processor.write_csv(weekly_output_file, weekly_csv_data)
    #     print(f"每周统计结果已保存到: {weekly_output_file}")
        
    #     # 保存每月统计
    #     monthly_output_file = os.path.join(current_dir, '每月称重统计.csv')
    #     monthly_csv_data = []
    #     for month, stats in monthly_results.items():
    #         monthly_csv_data.append({
    #             '月份': month,
    #             '称重次数': stats['count'],
    #             '重量均值(kg)': round(stats['mean'], 2),
    #             '重量标准差': round(stats['std_dev'], 2),
    #             '最小重量(kg)': round(stats['min'], 2),
    #             '最大重量(kg)': round(stats['max'], 2)
    #         })
        
    #     processor.write_csv(monthly_output_file, monthly_csv_data)
    #     print(f"每月统计结果已保存到: {monthly_output_file}")
        
    # except Exception as e:
    #     print(f"保存CSV文件时出错: {e}")
    
    return {
        'daily': daily_results,
        'weekly': weekly_results,
        'weekly_weekday_weekend': weekly_weekday_weekend_results,
        'monthly': monthly_results
    }


if __name__ == '__main__':
    # # 1、单台秤的称重失准异常分析
    # single_scale_example_usage()
    
    # 2、按时间分组的称重统计
    print("\n" + "="*100)
    print("开始按时间分组统计称重数据...")
    print("="*100)
    time_based_weight_statistics()
