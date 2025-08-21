import csv
import os

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


def example_usage():
    """示例用法"""
    processor = CSVProcessor()

    # 示例1: 基本读写操作
    print("示例1: 基本读写操作")
    sample_data = [
        {'姓名': '张三', '年龄': '25', '城市': '北京'},
        {'姓名': '李四', '年龄': '30', '城市': '上海'},
        {'姓名': '王五', '年龄': '35', '城市': '广州'}
    ]

    # 写入示例数据
    processor.write_csv('sample_data.csv', sample_data)
    print("已写入示例数据到 sample_data.csv")

    # 读取数据
    read_data = processor.read_csv('sample_data.csv')
    print("读取的数据:", read_data)

    # 示例2: 过滤数据
    print("\n示例2: 过滤数据")
    # 过滤年龄大于30的记录
    filtered_data = processor.filter_data(read_data, lambda x: int(x['年龄']) > 30)
    print("年龄大于30的记录:", filtered_data)

    # 示例3: 处理列数据
    print("\n示例3: 处理列数据")
    # 将年龄增加5岁
    processed_data = processor.process_column(read_data, '年龄', lambda x: str(int(x) + 5))
    print("年龄增加5岁后的数据:", processed_data)

    # 示例4: 聚合数据
    print("\n示例4: 聚合数据")
    # 按城市分组，计算平均年龄
    agg_data = processor.aggregate_data(read_data, '城市', '年龄', lambda x: sum(map(int, x)) / len(x))
    print("按城市分组的平均年龄:", agg_data)


if __name__ == '__main__':
    example_usage()