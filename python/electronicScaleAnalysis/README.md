# CSV数据处理脚本

这个Python脚本提供了一个功能完整的CSV文件处理器，可以轻松地读取、写入、过滤、处理和聚合CSV数据。

## 项目结构

```
project/
├── README.md
├── csv_processor.py
├── java/
├── python/
│   ├── .idea/
│   └── electronicScaleAnalysis/
│       └── main.py
├── sample_data.csv
└── test_data.csv
```


## 功能特点

- 读取CSV文件并转换为字典列表
- 将字典列表写入CSV文件
- 根据条件过滤数据
- 对指定列应用自定义处理函数
- 按指定列分组并聚合数据
- 提供完整的示例用法

## 使用方法

### 基本用法

```python
from csv_processor import CSVProcessor

# 创建处理器实例
processor = CSVProcessor()

# 读取CSV文件
data = processor.read_csv('input.csv')

# 处理数据...

# 写入CSV文件
processor.write_csv('output.csv', processed_data)
```

### 详细功能说明

#### 1. 读取CSV文件

```python
read_data = processor.read_csv(file_path)
```
- `file_path`: CSV文件路径
- 返回: 包含CSV数据的列表，每个元素是一行数据（字典形式）

#### 2. 写入CSV文件

```python
processor.write_csv(file_path, data, fieldnames=None)
```
- `file_path`: 输出文件路径
- `data`: 要写入的数据，每个元素是一行数据（字典形式）
- `fieldnames`: 可选，列名列表。如果为None，则从data的第一个元素获取

#### 3. 过滤数据

```python
filtered_data = processor.filter_data(data, condition_func)
```
- `data`: 要过滤的数据
- `condition_func`: 条件函数，返回True表示保留该行
- 返回: 过滤后的数据

示例：
```python
# 过滤年龄大于30的记录
filtered_data = processor.filter_data(data, lambda x: int(x['年龄']) > 30)
```

#### 4. 处理列数据

```python
processed_data = processor.process_column(data, column_name, process_func)
```
- `data`: 要处理的数据
- `column_name`: 列名
- `process_func`: 处理函数
- 返回: 处理后的数据

示例：
```python
# 将年龄增加5岁
processed_data = processor.process_column(data, '年龄', lambda x: str(int(x) + 5))
```

#### 5. 聚合数据

```python
agg_data = processor.aggregate_data(data, group_by_column, agg_column, agg_func)
```
- `data`: 要聚合的数据
- `group_by_column`: 分组列名
- `agg_column`: 要聚合的列名
- `agg_func`: 聚合函数
- 返回: 聚合结果（字典形式）

示例：
```python
# 按城市分组，计算平均年龄
agg_data = processor.aggregate_data(data, '城市', '年龄', lambda x: sum(map(int, x)) / len(x))
```

## 运行示例

脚本中包含了完整的示例用法，只需直接运行脚本即可查看效果：

```bash
python csv_processor.py
```

运行后将：
1. 创建一个示例CSV文件
2. 读取该文件
3. 展示过滤、列处理和聚合功能
4. 输出结果到控制台

## 扩展建议

1. 添加更多数据清洗功能（如处理缺失值、去重等）
2. 实现更复杂的聚合操作（如多列聚合、透视表等）
3. 添加数据可视化功能
4. 支持更大文件的分块处理

## 注意事项

1. 确保CSV文件的编码为UTF-8
2. 处理数值型数据时，可能需要进行类型转换
3. 对于大型CSV文件，可能需要优化内存使用