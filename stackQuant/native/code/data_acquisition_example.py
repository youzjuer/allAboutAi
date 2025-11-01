#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海欣食品数据获取示例
演示如何获取股票数据并进行量化分析
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def setup_matplotlib_for_plotting():
    """配置matplotlib绘图环境"""
    warnings.filterwarnings('default')
    plt.switch_backend("Agg")
    
    # 尝试多种seaborn样式，兼容不同版本
    available_styles = plt.style.available
    if "seaborn-v0_8" in available_styles:
        plt.style.use("seaborn-v0_8")
    elif "seaborn" in available_styles:
        plt.style.use("seaborn")
    elif "seaborn-darkgrid" in available_styles:
        plt.style.use("seaborn-darkgrid")
    else:
        # 使用默认样式
        plt.style.use("default")
    
    # 设置中文字体，兼容不同系统
    import platform
    system = platform.system()
    
    if system == "Windows":
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    elif system == "Darwin":  # macOS
        plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
    else:  # Linux
        plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Arial Unicode MS"]
    
    plt.rcParams["axes.unicode_minus"] = False

def load_yahoo_finance_data(symbol: str = "002702.SZ") -> Dict:
    """
    获取Yahoo Finance股票数据
    这里演示数据获取的逻辑，实际使用时需要调用相应的API
    """
    
    # 模拟从Yahoo Finance API获取的数据
    # 实际使用时，您需要使用以下方式获取数据：
    # 1. 使用yfinance库: yf.Ticker(symbol).history(period="2y")
    # 2. 使用requests调用Yahoo Finance API
    # 3. 使用其他金融数据API（如Alpha Vantage, Quandl等）
    
    print(f"正在获取{symbol}的股票数据...")
    
    # 这里是模拟的数据结构
    # 实际使用时，您需要替换为真实的API调用
    sample_data = {
        "success": True,
        "data": {
            "symbol": symbol,
            "prices": [
                {
                    "date": "2023-01-03",
                    "open": 6.90,
                    "high": 6.90,
                    "low": 6.67,
                    "close": 6.76,
                    "volume": 27221416
                },
                {
                    "date": "2023-01-04", 
                    "open": 6.67,
                    "high": 7.32,
                    "low": 6.60,
                    "close": 6.95,
                    "volume": 48404024
                }
                # ... 更多数据
            ]
        }
    }
    
    return sample_data

def get_stock_info(symbol: str = "002702.SZ") -> Dict:
    """获取股票基本信息"""
    
    # 模拟股票基本信息
    # 实际使用时需要调用相应的API
    sample_info = {
        "success": True,
        "data": {
            "symbol": symbol,
            "market_cap": 5000000000,  # 50亿市值
            "pe_ratio": 25.5,
            "forward_pe": 22.1,
            "dividend_yield": 0.025,
            "beta": 1.2,
            "fifty_two_week": {
                "high": 8.45,
                "low": 4.20
            },
            "moving_averages": {
                "sma_50": 5.85,
                "sma_200": 6.12
            },
            "volume": 2500000
        }
    }
    
    return sample_info

def get_stock_basic_info(symbol: str = "002702.SZ") -> Dict:
    """获取股票基本信息 - 用于区分价格数据"""
    
    # 模拟股票基本信息
    # 实际使用时需要调用相应的API
    sample_info = {
        "success": True,
        "data": {
            "symbol": symbol,
            "market_cap": 5000000000,  # 50亿市值
            "pe_ratio": 25.5,
            "forward_pe": 22.1,
            "dividend_yield": 0.025,
            "beta": 1.2,
            "fifty_two_week": {
                "high": 8.45,
                "low": 4.20
            },
            "moving_averages": {
                "sma_50": 5.85,
                "sma_200": 6.12
            },
            "volume": 2500000
        }
    }
    
    return sample_info

def get_financial_data(symbol: str = "002702.SZ") -> Dict:
    """获取财务数据"""
    
    # 模拟财务数据
    # 实际使用时需要调用相应的API
    sample_financial = {
        "success": True,
        "data": {
            "symbol": symbol,
            "price": {
                "current": 4.81,
                "target": 5.50
            },
            "recommendation": {
                "rating": "Hold",
                "target_price": 5.50
            },
            "financial_metrics": {
                "current_ratio": 1.8,
                "quick_ratio": 1.2,
                "debt_to_equity": 45.2,
                "total_cash": 800000000
            },
            "profitability": {
                "gross_margin": 0.28,
                "operating_margin": 0.12,
                "profit_margin": 0.08,
                "return_on_equity": 0.15,
                "return_on_assets": 0.09
            },
            "growth": {
                "revenue_growth": 0.05,
                "earnings_growth": 0.08
            },
            "returns": {
                "return_on_equity": 0.15,
                "return_on_assets": 0.09,
                "return_on_invested_capital": 0.12
            },
            "cash_flow": {
                "operating_cash_flow": 450000000,
                "free_cash_flow": 320000000
            }
        }
    }
    
    return sample_financial

def save_data_to_files(price_data: Dict, info_data: Dict, financial_data: Dict):
    """保存数据到文件"""
    
    # 创建数据目录
    import os
    os.makedirs('data', exist_ok=True)
    
    # 保存价格数据
    with open('data/haixin_price.json', 'w', encoding='utf-8') as f:
        json.dump(price_data, f, ensure_ascii=False, indent=2)
    
    # 保存基本信息
    with open('data/haixin_info.json', 'w', encoding='utf-8') as f:
        json.dump(info_data, f, ensure_ascii=False, indent=2)
    
    # 保存财务数据
    with open('data/haixin_financial.json', 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, ensure_ascii=False, indent=2)
    
    print("数据已保存到文件:")
    print("- data/haixin_price.json (价格数据)")
    print("- data/haixin_info.json (基本信息)")
    print("- data/haixin_financial.json (财务数据)")

def load_data_from_files():
    """从文件加载数据"""
    
    # 加载价格数据
    with open('data/haixin_price.json', 'r', encoding='utf-8') as f:
        price_data = json.load(f)
    
    # 加载基本信息
    with open('data/haixin_info.json', 'r', encoding='utf-8') as f:
        info_data = json.load(f)
    
    # 加载财务数据
    with open('data/haixin_financial.json', 'r', encoding='utf-8') as f:
        financial_data = json.load(f)
    
    return price_data, info_data, financial_data

def process_price_data(price_data: Dict) -> pd.DataFrame:
    """处理价格数据为DataFrame"""
    
    # 获取价格数据
    prices = price_data['data']['prices']
    
    # 转换为DataFrame
    df = pd.DataFrame(prices)
    
    # 转换日期格式
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # 排序
    df.sort_index(inplace=True)
    
    # 去除空值
    df.dropna(inplace=True)
    
    print(f"价格数据处理完成:")
    print(f"- 数据期间: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"- 总交易日: {len(df)}天")
    print(f"- 最新价格: ¥{df['close'].iloc[-1]:.2f}")
    
    return df

def calculate_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """计算基础技术指标"""
    
    # 移动平均线
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_60'] = df['close'].rolling(window=60).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema_12 = df['close'].ewm(span=12).mean()
    ema_26 = df['close'].ewm(span=26).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    # 布林带
    sma_20 = df['close'].rolling(window=20).mean()
    std_20 = df['close'].rolling(window=20).std()
    df['bb_upper'] = sma_20 + (std_20 * 2)
    df['bb_lower'] = sma_20 - (std_20 * 2)
    
    # 价格变化率
    df['price_change'] = df['close'].pct_change()
    df['price_change_5d'] = df['close'].pct_change(5)
    
    print("技术指标计算完成")
    
    return df

def simple_backtest(df: pd.DataFrame, initial_capital: float = 100000) -> Dict:
    """简单的回测示例"""
    
    # 基于RSI的简单策略
    signals = pd.Series(0, index=df.index)
    signals[df['rsi'] < 30] = 1  # 超卖买入
    signals[df['rsi'] > 70] = -1  # 超买卖出
    
    # 回测
    portfolio_value = []
    cash = initial_capital
    shares = 0
    
    for i, (date, signal) in enumerate(signals.items()):
        current_price = df.loc[date, 'close']
        
        if signal == 1 and cash > current_price:  # 买入
            shares_to_buy = int(cash * 0.95 / current_price)
            if shares_to_buy > 0:
                shares += shares_to_buy
                cash -= shares_to_buy * current_price
        
        elif signal == -1 and shares > 0:  # 卖出
            cash += shares * current_price
            shares = 0
        
        # 计算组合价值
        total_value = cash + shares * current_price
        portfolio_value.append(total_value)
    
    # 计算绩效指标
    total_return = (portfolio_value[-1] / initial_capital - 1) * 100
    benchmark_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
    
    results = {
        'initial_capital': initial_capital,
        'final_value': portfolio_value[-1],
        'total_return': total_return,
        'benchmark_return': benchmark_return,
        'excess_return': total_return - benchmark_return,
        'buy_signals': (signals == 1).sum(),
        'sell_signals': (signals == -1).sum()
    }
    
    return results

def create_simple_chart(df: pd.DataFrame, save_path: str = 'charts/simple_analysis.png'):
    """创建简单的分析图表"""
    
    setup_matplotlib_for_plotting()
    
    # 创建图表目录
    import os
    os.makedirs('charts', exist_ok=True)
    
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    
    # 价格和移动平均线
    axes[0].plot(df.index, df['close'], label='收盘价', linewidth=2)
    axes[0].plot(df.index, df['sma_5'], label='MA5', alpha=0.7)
    axes[0].plot(df.index, df['sma_20'], label='MA20', alpha=0.7)
    axes[0].set_title('海欣食品股价走势', fontsize=16, fontweight='bold')
    axes[0].set_ylabel('价格 (元)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # RSI
    axes[1].plot(df.index, df['rsi'], label='RSI', linewidth=2, color='purple')
    axes[1].axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线')
    axes[1].axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线')
    axes[1].set_title('RSI指标', fontsize=14)
    axes[1].set_ylabel('RSI')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # MACD
    axes[2].plot(df.index, df['macd'], label='MACD', linewidth=2)
    axes[2].plot(df.index, df['macd_signal'], label='信号线', linewidth=2)
    axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[2].set_title('MACD指标', fontsize=14)
    axes[2].set_ylabel('MACD')
    axes[2].set_xlabel('日期')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"图表已保存: {save_path}")

def main():
    """主函数 - 完整的数据获取和分析流程"""
    
    print("=== 海欣食品数据获取和分析示例 ===\n")
    
    try:
        # 1. 获取数据
        print("1. 获取股票数据...")
        # 使用现有的真实数据
        price_data, info_data, financial_data = load_data_from_files()
        
        print("数据获取完成，使用现有数据文件")
        
        # 4. 处理价格数据
        print("4. 处理价格数据...")
        df = process_price_data(price_data)
        
        # 5. 计算技术指标
        print("5. 计算技术指标...")
        df = calculate_basic_indicators(df)
        
        # 6. 简单回测
        print("6. 运行简单回测...")
        backtest_results = simple_backtest(df)
        
        print(f"\n回测结果:")
        print(f"初始资金: ¥{backtest_results['initial_capital']:,.2f}")
        print(f"最终价值: ¥{backtest_results['final_value']:,.2f}")
        print(f"总收益率: {backtest_results['total_return']:.2f}%")
        print(f"基准收益率: {backtest_results['benchmark_return']:.2f}%")
        print(f"超额收益: {backtest_results['excess_return']:.2f}%")
        print(f"买入信号: {backtest_results['buy_signals']}次")
        print(f"卖出信号: {backtest_results['sell_signals']}次")
        
        # 7. 创建图表
        print("7. 生成分析图表...")
        create_simple_chart(df)
        
        print("\n=== 分析完成 ===")
        print("文件输出:")
        print("- data/haixin_price.json (价格数据)")
        print("- data/haixin_info.json (基本信息)")
        print("- data/haixin_financial.json (财务数据)")
        print("- charts/simple_analysis.png (分析图表)")
        
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()