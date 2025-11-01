#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matplotlib配置测试脚本
验证matplotlib设置是否正常工作
"""

import matplotlib.pyplot as plt
import numpy as np
import platform

def test_matplotlib_setup():
    """测试matplotlib配置"""
    print("=== matplotlib配置测试 ===")
    
    # 检查matplotlib版本
    print(f"matplotlib版本: {plt.matplotlib.__version__}")
    print(f"Python版本: {platform.python_version()}")
    print(f"操作系统: {platform.system()}")
    
    # 检查可用的样式
    print(f"\n可用的matplotlib样式:")
    for style in plt.style.available[:10]:  # 只显示前10个
        print(f"  - {style}")
    if len(plt.style.available) > 10:
        print(f"  ... 还有{len(plt.style.available) - 10}个样式")
    
    # 测试样式设置
    print(f"\n测试样式设置...")
    try:
        # 尝试多种seaborn样式
        if "seaborn-v0_8" in plt.style.available:
            plt.style.use("seaborn-v0_8")
            print("✓ 使用 seaborn-v0_8 样式成功")
        elif "seaborn" in plt.style.available:
            plt.style.use("seaborn")
            print("✓ 使用 seaborn 样式成功")
        elif "seaborn-darkgrid" in plt.style.available:
            plt.style.use("seaborn-darkgrid")
            print("✓ 使用 seaborn-darkgrid 样式成功")
        else:
            plt.style.use("default")
            print("✓ 使用 default 样式成功")
            
    except Exception as e:
        print(f"✗ 样式设置失败: {e}")
        plt.style.use("default")
    
    # 测试中文字体设置
    print(f"\n测试中文字体设置...")
    system = platform.system()
    if system == "Windows":
        fonts = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    elif system == "Darwin":  # macOS
        fonts = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
    else:  # Linux
        fonts = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Arial Unicode MS"]
    
    plt.rcParams["font.sans-serif"] = fonts
    plt.rcParams["axes.unicode_minus"] = False
    print(f"✓ 中文字体设置完成: {fonts}")
    
    # 测试绘图
    print(f"\n测试绘图功能...")
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, label='sin(x)')
        ax.set_title('matplotlib测试图')
        ax.set_xlabel('x轴')
        ax.set_ylabel('y轴')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存测试图
        plt.savefig('test_plot.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✓ 绘图测试成功，已保存为 test_plot.png")
        
    except Exception as e:
        print(f"✗ 绘图测试失败: {e}")
        return False
    
    print(f"\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_matplotlib_setup()