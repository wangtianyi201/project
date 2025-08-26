import csv
import os
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy import stats
import numpy as np

# 设置matplotlib支持中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
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


if __name__ == '__main__':
    # 1、单台秤的称重失准异常分析
    single_scale_example_usage()
