#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
称重数据可视化工具启动脚本
运行此脚本将生成并打开可视化网页
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from web_visualization import WebVisualizationGenerator
    
    def main():
        """主函数"""
        print("="*80)
        print("🎯 称重数据可视化工具")
        print("="*80)
        print("正在启动可视化工具...")
        print()
        
        # 创建可视化生成器
        generator = WebVisualizationGenerator()
        
        # 生成可视化网页
        html_file = generator.generate_visualization()
        
        if html_file:
            print("\n" + "="*80)
            print("✅ 可视化网页生成成功!")
            print("="*80)
            print(f"📁 文件位置: {html_file}")
            print(f"🌐 网页已在浏览器中打开")
            print(f"💡 如果没有自动打开，请手动打开文件")
            print()
            print("🎉 享受您的数据可视化体验!")
        else:
            print("\n" + "="*80)
            print("❌ 可视化网页生成失败")
            print("="*80)
            print("请检查:")
            print("1. 数据文件是否存在")
            print("2. 数据文件格式是否正确")
            print("3. 是否有足够的权限创建文件")
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有必要的文件都在同一目录下")
except Exception as e:
    print(f"❌ 运行错误: {e}")
    print("请检查错误信息并重试")
