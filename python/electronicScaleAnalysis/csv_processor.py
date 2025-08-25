import csv
import os
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict

# 设置matplotlib支持中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def calculate_z_scores(test_ratios, reference_ratios):
    """计算测试数据比值相对于参考数据比值的Z-score，并判断异常程度

    Args:
        test_ratios (list): 测试数据的比值列表
        reference_ratios (list): 参考数据的比值列表

    Returns:
        list: 包含Z-score值和异常程度的字典列表
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
    for ratio in test_ratios:
        z_score = (ratio - ref_mean) / ref_std
        abs_z = abs(z_score)
        if abs_z > 3:
            anomaly = "重度异常"
        elif abs_z > 2:
            anomaly = "轻度异常"
        else:
            anomaly = "正常"
        z_score_results.append({
            'z_score': z_score,
            'anomaly': anomaly
        })

    return z_score_results


def analyze_file_and_get_ratios(file_path, ad_column='称重AD值', zero_ad_column='零点AD值', weight_column='重量(kg)'):
    """分析文件并获取比值列表

    Args:
        file_path (str): 文件路径
        ad_column (str): 称重AD值列名
        zero_ad_column (str): 零点AD值列名
        weight_column (str): 重量值列名

    Returns:
        list: 比值列表
    """
    processor = CSVProcessor()

    try:
        data = processor.read_csv(file_path)
        print(f"成功读取 {file_path} 中的 {len(data)} 条记录")
    except FileNotFoundError as e:
        print(e)
        return []

    valid_ratios = []

    for row in data:
        try:
            ad_value = float(row[ad_column])
            zero_ad_value = float(row[zero_ad_column])
            weight_value = float(row[weight_column])

            k_value = ad_value - zero_ad_value
            ratio = k_value / weight_value / 1000 if weight_value != 0 else 0

            valid_ratios.append(ratio)
        except (ValueError, KeyError) as e:
            continue

    return valid_ratios


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
    test_file = os.path.join(current_dir, '测试数据.csv')
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
    print("\n设备数据比值的描述性分析:")
    analyze_weight_data(device_file)

    
    # 分析文件并获取比值
    print("正在分析测试数据文件...")
    test_ratios = analyze_file_and_get_ratios(test_file)
    
    print("正在分析设备数据文件...")
    device_ratios = analyze_file_and_get_ratios(device_file)
    
    # 检查是否有足够的有效比值
    if not test_ratios:
        print("错误: 测试数据中没有有效比值")
        return
    
    if len(device_ratios) < 2:
        print("错误: 设备数据中有效比值不足")
        return

    print(test_ratios)
    print("##########")
    print(device_ratios)

    # 计算Z-score
    z_score_results = calculate_z_scores(test_ratios, device_ratios)
    
    if z_score_results:
        print("\nZ-score计算结果:")
        print("=" * 60)
        print(f"{'数据点':<10}{'Z-score值':<15}{'异常程度':<15}")
        print("=" * 60)
        for i, result in enumerate(z_score_results):
            z = result['z_score']
            anomaly = result['anomaly']
            print(f"{i+1:<10}{z:<15.4f}{anomaly:<15}")


if __name__ == '__main__':
    single_scale_example_usage()
