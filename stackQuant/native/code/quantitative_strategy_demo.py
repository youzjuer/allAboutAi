#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版海欣食品量化策略示例
演示如何使用量化分析系统
"""

import sys
import os
sys.path.append('/workspace/code')

from haixin_quantitative_analysis import (
    StockDataProcessor, TechnicalAnalyzer, FundamentalAnalyzer,
    QuantitativeStrategies, BacktestEngine, RiskManager, 
    VisualizationEngine, QuantitativeAnalysisReport
)

def quick_analysis_demo():
    """快速分析演示"""
    print("=== 海欣食品量化策略演示 ===\n")
    
    try:
        # 1. 加载数据
        print("1. 加载海欣食品数据...")
        processor = StockDataProcessor(
            '/workspace/data/haixin_price.json',
            '/workspace/data/haixin_info.json', 
            '/workspace/data/haixin_financial.json'
        )
        processor.load_data()
        
        # 2. 技术分析
        print("2. 计算技术指标...")
        technical_analyzer = TechnicalAnalyzer(processor.price_df)
        technical_df = technical_analyzer.calculate_all_indicators()
        
        # 3. 基本面分析
        print("3. 分析基本面...")
        fundamental_analyzer = FundamentalAnalyzer(processor.info_data, processor.financial_data)
        fundamental_analysis = fundamental_analyzer.analyze_financial_health()
        
        # 4. 策略信号
        print("4. 生成交易信号...")
        strategy = QuantitativeStrategies(technical_df)
        
        # 演示不同的策略
        strategies = {
            '均值回归': strategy.mean_reversion_strategy(),
            '动量策略': strategy.momentum_strategy(),
            '布林带策略': strategy.bollinger_bands_strategy(),
            '双均线策略': strategy.dual_moving_average_strategy(),
            '综合策略': strategy.combined_strategy()
        }
        
        # 5. 回测每个策略
        print("5. 回测各策略...")
        results = {}
        for name, signals in strategies.items():
            backtest = BacktestEngine(technical_df)
            backtest_results, _ = backtest.run_backtest(signals)
            results[name] = backtest_results
            
            print(f"\n{name}策略结果:")
            print(f"  总收益率: {backtest_results['total_return']:.2f}%")
            print(f"  年化收益率: {backtest_results['annual_return']:.2f}%")
            print(f"  夏普比率: {backtest_results['sharpe_ratio']:.3f}")
            print(f"  最大回撤: {backtest_results['max_drawdown']:.2f}%")
            print(f"  胜率: {backtest_results['win_rate']:.1f}%")
        
        # 6. 风险分析
        print("\n6. 风险分析...")
        risk_manager = RiskManager(technical_df)
        risk_analysis = risk_manager.risk_assessment()
        
        print(f"风险等级: {risk_analysis['risk_level']}")
        print(f"波动率: {risk_analysis['volatility']:.2f}%")
        print(f"VaR (5%): {risk_analysis['var_5']:.2f}%")
        print(f"最大回撤: {risk_analysis['max_drawdown']:.2f}%")
        
        # 7. 策略对比
        print("\n7. 策略对比总结:")
        print("=" * 60)
        print(f"{'策略名称':<12} {'总收益率':<10} {'夏普比率':<10} {'最大回撤':<10}")
        print("=" * 60)
        
        for name, result in results.items():
            print(f"{name:<12} {result['total_return']:<10.2f} {result['sharpe_ratio']:<10.3f} {result['max_drawdown']:<10.2f}")
        
        # 8. 投资建议
        print("\n8. 投资建议:")
        print("=" * 40)
        
        # 基于技术指标的建议
        latest_rsi = technical_df['rsi'].iloc[-1]
        latest_macd = technical_df['macd'].iloc[-1]
        latest_signal = technical_df['macd_signal'].iloc[-1]
        
        print(f"当前RSI: {latest_rsi:.2f}")
        if latest_rsi > 70:
            print("  → RSI显示超买，建议谨慎")
        elif latest_rsi < 30:
            print("  → RSI显示超卖，可能存在反弹机会")
        else:
            print("  → RSI处于正常区间")
        
        print(f"当前MACD: {latest_macd:.4f}")
        if latest_macd > latest_signal:
            print("  → MACD呈现买入信号")
        else:
            print("  → MACD呈现卖出信号")
        
        # 基于基本面的建议
        profitability_score = fundamental_analysis['profitability']['score']
        print(f"\n基本面状况: {profitability_score}")
        if profitability_score == '亏损':
            print("  → 公司目前处于亏损状态，需关注盈利能力改善")
        elif profitability_score == '一般':
            print("  → 公司盈利能力一般，谨慎投资")
        else:
            print("  → 公司盈利能力良好")
        
        # 风险建议
        print(f"\n风险等级: {risk_analysis['risk_level']}")
        if risk_analysis['risk_level'] == '高':
            print("  → 高风险投资，建议小仓位操作")
            print("  → 建议设置严格的止损位")
        elif risk_analysis['risk_level'] == '中':
            print("  → 中等风险，可适量配置")
        else:
            print("  → 风险相对较低，可适当增加仓位")
        
        print("\n=== 分析完成 ===")
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def custom_strategy_example():
    """自定义策略示例"""
    print("\n=== 自定义策略示例 ===")
    
    try:
        # 加载数据
        processor = StockDataProcessor(
            '/workspace/data/haixin_price.json',
            '/workspace/data/haixin_info.json', 
            '/workspace/data/haixin_financial.json'
        )
        processor.load_data()
        
        # 技术分析
        technical_analyzer = TechnicalAnalyzer(processor.price_df)
        technical_df = technical_analyzer.calculate_all_indicators()
        
        # 自定义策略：基于价格突破和成交量的策略
        def custom_breakout_strategy(df):
            signals = pd.Series(0, index=df.index)
            
            # 价格突破20日高点且成交量放大
            price_breakout = df['close'] > df['close'].rolling(20).max()
            volume_surge = df['volume'] > df['volume'].rolling(20).mean() * 1.5
            
            signals[price_breakout & volume_surge] = 1
            
            # 价格跌破20日低点且成交量放大
            price_breakdown = df['close'] < df['close'].rolling(20).min()
            signals[price_breakdown & volume_surge] = -1
            
            return signals
        
        import pandas as pd
        custom_signals = custom_breakout_strategy(technical_df)
        
        # 回测自定义策略
        backtest = BacktestEngine(technical_df)
        backtest_results, _ = backtest.run_backtest(custom_signals)
        
        print("自定义突破策略结果:")
        print(f"  总收益率: {backtest_results['total_return']:.2f}%")
        print(f"  年化收益率: {backtest_results['annual_return']:.2f}%")
        print(f"  夏普比率: {backtest_results['sharpe_ratio']:.3f}")
        print(f"  最大回撤: {backtest_results['max_drawdown']:.2f}%")
        print(f"  胜率: {backtest_results['win_rate']:.1f}%")
        
        # 信号统计
        buy_signals = (custom_signals == 1).sum()
        sell_signals = (custom_signals == -1).sum()
        print(f"\n信号统计:")
        print(f"  买入信号: {buy_signals}次")
        print(f"  卖出信号: {sell_signals}次")
        print(f"  总交易日: {len(custom_signals)}天")
        print(f"  信号频率: {(buy_signals + sell_signals) / len(custom_signals) * 100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"自定义策略分析错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行快速分析演示
    quick_analysis_demo()
    
    # 运行自定义策略示例
    custom_strategy_example()