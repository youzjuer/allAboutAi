#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多股票量化分析系统演示版
使用本地数据演示多股票分析功能
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import glob

def setup_matplotlib_for_plotting():
    """
    Setup matplotlib and seaborn for plotting with proper configuration.
    Call this function before creating any plots to ensure proper rendering.
    """
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
    
    sns.set_palette("husl")
    
    # 设置中文字体，兼容不同系统
    import platform
    system = platform.system()
    
    if system == "Windows":
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
    elif system == "Darwin":  # macOS
        plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS"]
    else:  # Linux
        plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "Arial Unicode MS"]

class TechnicalAnalyzer:
    """技术分析类"""
    
    def __init__(self, price_df: pd.DataFrame):
        self.price_df = price_df.copy()
        
    def calculate_indicators(self):
        """计算技术指标"""
        df = self.price_df.copy()
        
        # 标准化列名 - 处理大小写问题
        column_mapping = {}
        for col in df.columns:
            if col.lower() in ['volume', 'vol']:
                column_mapping[col] = 'Volume'
            elif col.lower() in ['open', 'high', 'low', 'close']:
                column_mapping[col] = col.lower()
        
        df = df.rename(columns=column_mapping)
        
        # 移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # 布林带
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # 成交量移动平均
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        return df

class FundamentalAnalyzer:
    """基本面分析类"""
    
    def __init__(self, info_data: Dict, financial_data: Optional[Dict] = None):
        self.info_data = info_data
        self.financial_data = financial_data
    
    def get_company_overview(self) -> Dict:
        """获取公司概况"""
        if not self.info_data:
            return {}
        
        overview = {
            '公司名称': self.info_data.get('longName', 'N/A'),
            '行业': self.info_data.get('industry', 'N/A'),
            '市值': self.info_data.get('marketCap', 0),
            '员工数': self.info_data.get('fullTimeEmployees', 'N/A'),
            '成立时间': self.info_data.get('dateFounded', 'N/A'),
            '公司地址': self.info_data.get('address1', 'N/A'),
            '公司简介': self.info_data.get('longBusinessSummary', 'N/A')[:200] + '...' if self.info_data.get('longBusinessSummary') else 'N/A'
        }
        return overview
    
    def get_valuation_metrics(self) -> Dict:
        """获取估值指标"""
        if not self.info_data:
            return {}
        
        metrics = {
            '市盈率(PE)': self.info_data.get('trailingPE', 'N/A'),
            '市净率(PB)': self.info_data.get('priceToBook', 'N/A'),
            '股息收益率': self.info_data.get('dividendYield', 'N/A'),
            '贝塔系数': self.info_data.get('beta', 'N/A'),
            '52周最高价': self.info_data.get('fiftyTwoWeekHigh', 'N/A'),
            '52周最低价': self.info_data.get('fiftyTwoWeekLow', 'N/A'),
            '目标价': self.info_data.get('targetMeanPrice', 'N/A'),
            '分析师评级': self.info_data.get('recommendationMean', 'N/A')
        }
        return metrics

class QuantitativeStrategies:
    """量化策略类"""
    
    def __init__(self, technical_df: pd.DataFrame):
        self.df = technical_df.copy()
    
    def mean_reversion_strategy(self) -> pd.Series:
        """均值回归策略"""
        signals = pd.Series(0, index=self.df.index)
        
        # RSI超买超卖信号
        rsi_oversold = self.df['RSI'] < 30
        rsi_overbought = self.df['RSI'] > 70
        
        # 布林带信号
        bb_oversold = self.df['close'] < self.df['BB_lower']
        bb_overbought = self.df['close'] > self.df['BB_upper']
        
        # 买入信号：RSI超卖且价格触及布林带下轨
        buy_signals = rsi_oversold & bb_oversold
        signals[buy_signals] = 1
        
        # 卖出信号：RSI超买且价格触及布林带上轨
        sell_signals = rsi_overbought & bb_overbought
        signals[sell_signals] = -1
        
        return signals
    
    def momentum_strategy(self) -> pd.Series:
        """动量策略"""
        signals = pd.Series(0, index=self.df.index)
        
        # 金叉死叉信号
        golden_cross = (self.df['MA5'] > self.df['MA20']) & (self.df['MA5'].shift(1) <= self.df['MA20'].shift(1))
        death_cross = (self.df['MA5'] < self.df['MA20']) & (self.df['MA5'].shift(1) >= self.df['MA20'].shift(1))
        
        # MACD信号
        macd_bullish = (self.df['MACD'] > self.df['MACD_signal']) & (self.df['MACD'].shift(1) <= self.df['MACD_signal'].shift(1))
        macd_bearish = (self.df['MACD'] < self.df['MACD_signal']) & (self.df['MACD'].shift(1) >= self.df['MACD_signal'].shift(1))
        
        # 综合信号
        buy_signals = golden_cross | macd_bullish
        sell_signals = death_cross | macd_bearish
        
        signals[buy_signals] = 1
        signals[sell_signals] = -1
        
        return signals
    
    def bollinger_bands_strategy(self) -> pd.Series:
        """布林带策略"""
        signals = pd.Series(0, index=self.df.index)
        
        # 价格触及布林带边界
        buy_signals = self.df['close'] < self.df['BB_lower']
        sell_signals = self.df['close'] > self.df['BB_upper']
        
        signals[buy_signals] = 1
        signals[sell_signals] = -1
        
        return signals
    
    def dual_ma_strategy(self) -> pd.Series:
        """双均线策略"""
        signals = pd.Series(0, index=self.df.index)
        
        # 短期均线上穿长期均线买入，下穿卖出
        golden_cross = (self.df['MA5'] > self.df['MA50']) & (self.df['MA5'].shift(1) <= self.df['MA50'].shift(1))
        death_cross = (self.df['MA5'] < self.df['MA50']) & (self.df['MA5'].shift(1) >= self.df['MA50'].shift(1))
        
        signals[golden_cross] = 1
        signals[death_cross] = -1
        
        return signals
    
    def combined_strategy(self) -> pd.Series:
        """组合策略"""
        # 各个策略的信号
        mean_reversion = self.mean_reversion_strategy()
        momentum = self.momentum_strategy()
        bollinger = self.bollinger_bands_strategy()
        dual_ma = self.dual_ma_strategy()
        
        # 综合信号（多数投票）
        combined = mean_reversion + momentum + bollinger + dual_ma
        
        # 设定阈值
        signals = pd.Series(0, index=self.df.index)
        signals[combined >= 2] = 1  # 至少2个策略看涨
        signals[combined <= -2] = -1  # 至少2个策略看跌
        
        return signals

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, technical_df: pd.DataFrame, initial_capital: float = 100000):
        self.df = technical_df.copy()
        self.initial_capital = initial_capital
    
    def run_backtest(self, signals: pd.Series) -> Tuple[Dict, pd.DataFrame]:
        """运行回测"""
        df = self.df.copy()
        df['signal'] = signals
        df['position'] = df['signal'].shift(1).fillna(0)  # 信号延迟一天执行
        
        # 计算收益率
        df['market_return'] = df['close'].pct_change()
        df['strategy_return'] = df['position'] * df['market_return']
        
        # 计算累计收益
        df['cumulative_market'] = (1 + df['market_return'].fillna(0)).cumprod()
        df['cumulative_strategy'] = (1 + df['strategy_return'].fillna(0)).cumprod()
        
        # 计算资金曲线
        df['portfolio_value'] = self.initial_capital * df['cumulative_strategy']
        
        # 计算指标
        total_return = (df['cumulative_strategy'].iloc[-1] - 1) * 100
        benchmark_return = (df['cumulative_market'].iloc[-1] - 1) * 100
        
        # 年化收益率
        trading_days = len(df)
        years = trading_days / 252
        annual_return = ((df['cumulative_strategy'].iloc[-1]) ** (1/years) - 1) * 100
        
        # 夏普比率
        strategy_returns = df['strategy_return'].dropna()
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
        
        # 最大回撤
        rolling_max = df['cumulative_strategy'].expanding().max()
        drawdown = (df['cumulative_strategy'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        results = {
            'total_return': total_return,
            'benchmark_return': benchmark_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': strategy_returns.std() * np.sqrt(252) * 100,
            'win_rate': (strategy_returns > 0).mean() * 100
        }
        
        return results, df

class RiskManager:
    """风险管理类"""
    
    def __init__(self, technical_df: pd.DataFrame):
        self.df = technical_df.copy()
    
    def risk_assessment(self) -> Dict:
        """风险评估"""
        returns = self.df['close'].pct_change().dropna()
        
        # 计算风险指标
        volatility = returns.std() * np.sqrt(252) * 100
        var_95 = returns.quantile(0.05) * 100
        var_99 = returns.quantile(0.01) * 100
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # 风险等级
        if max_drawdown > -20 or volatility > 40:
            risk_level = "高风险"
        elif max_drawdown > -10 or volatility > 25:
            risk_level = "中等风险"
        else:
            risk_level = "低风险"
        
        return {
            'volatility': volatility,
            'var_95': var_95,
            'var_99': var_99,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level
        }

class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self, technical_df: pd.DataFrame, stock_code: str, output_dir: str = "charts"):
        self.df = technical_df.copy()
        self.stock_code = stock_code
        self.output_dir = output_dir
        self.initial_capital = 100000
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置matplotlib
        setup_matplotlib_for_plotting()
    
    def plot_price_and_indicators(self):
        """绘制价格和技术指标"""
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 价格和移动平均线
        axes[0].plot(self.df.index, self.df['close'], label='收盘价', linewidth=2)
        axes[0].plot(self.df.index, self.df['MA5'], label='MA5', alpha=0.7)
        axes[0].plot(self.df.index, self.df['MA20'], label='MA20', alpha=0.7)
        axes[0].plot(self.df.index, self.df['MA50'], label='MA50', alpha=0.7)
        axes[0].fill_between(self.df.index, self.df['BB_upper'], self.df['BB_lower'], alpha=0.2, label='布林带')
        axes[0].set_title(f'{self.stock_code} 价格走势和技术指标')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # RSI
        axes[1].plot(self.df.index, self.df['RSI'], label='RSI', color='purple')
        axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线')
        axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线')
        axes[1].set_title('RSI 相对强弱指标')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # MACD
        axes[2].plot(self.df.index, self.df['MACD'], label='MACD', color='blue')
        axes[2].plot(self.df.index, self.df['MACD_signal'], label='信号线', color='red')
        axes[2].bar(self.df.index, self.df['MACD_histogram'], label='MACD柱', alpha=0.6)
        axes[2].set_title('MACD 指标')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{self.stock_code.replace(".", "_")}_price_indicators.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_volume_analysis(self):
        """绘制成交量分析"""
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # 成交量
        axes[0].bar(self.df.index, self.df['Volume'], alpha=0.7, label='成交量')
        axes[0].plot(self.df.index, self.df['Volume_MA'], color='red', label='成交量均线')
        axes[0].set_title(f'{self.stock_code} 成交量分析')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 价格和成交量关系
        colors = ['red' if close >= open else 'green' for close, open in zip(self.df['close'], self.df['open'])]
        axes[1].bar(self.df.index, self.df['Volume'], color=colors, alpha=0.7)
        axes[1].set_title('成交量与价格变化')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{self.stock_code.replace(".", "_")}_volume_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_strategy_performance(self, backtest_results: Dict):
        """绘制策略表现"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 累计收益对比
        axes[0, 0].plot(self.df.index, self.df['cumulative_market'], label='市场基准', linewidth=2)
        axes[0, 0].plot(self.df.index, self.df['cumulative_strategy'], label='策略收益', linewidth=2)
        axes[0, 0].set_title('累计收益率对比')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 资金曲线
        axes[0, 1].plot(self.df.index, self.df['portfolio_value'], label='资金曲线', linewidth=2, color='green')
        axes[0, 1].axhline(y=self.initial_capital, color='red', linestyle='--', alpha=0.7, label='初始资金')
        axes[0, 1].set_title('资金曲线')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 回撤分析
        cumulative = self.df['cumulative_strategy']
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max * 100
        axes[1, 0].fill_between(self.df.index, drawdown, 0, alpha=0.7, color='red')
        axes[1, 0].set_title('回撤分析')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 策略信号
        buy_signals = self.df[self.df['signal'] == 1]
        sell_signals = self.df[self.df['signal'] == -1]
        
        axes[1, 1].plot(self.df.index, self.df['close'], label='价格', alpha=0.7)
        axes[1, 1].scatter(buy_signals.index, buy_signals['close'], color='green', marker='^', s=50, label='买入信号')
        axes[1, 1].scatter(sell_signals.index, sell_signals['close'], color='red', marker='v', s=50, label='卖出信号')
        axes[1, 1].set_title('交易信号')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/{self.stock_code.replace(".", "_")}_strategy_performance.png', dpi=300, bbox_inches='tight')
        plt.close()

class QuantitativeAnalysisReport:
    """量化分析报告生成器"""
    
    def __init__(self, stock_code: str, price_df: pd.DataFrame, fundamental_analysis: Dict, 
                 technical_df: pd.DataFrame, backtest_results: Dict, risk_analysis: Dict):
        self.stock_code = stock_code
        self.price_df = price_df
        self.fundamental_analysis = fundamental_analysis
        self.technical_df = technical_df
        self.backtest_results = backtest_results
        self.risk_analysis = risk_analysis
    
    def generate_report(self) -> str:
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"reports/{self.stock_code.replace('.', '_')}_analysis_{timestamp}.md"
        
        # 创建报告目录
        os.makedirs("reports", exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# {self.stock_code} 量化分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 执行摘要
            f.write("## 执行摘要\n\n")
            f.write(f"- **当前股价**: ¥{self.price_df['close'].iloc[-1]:.2f}\n")
            f.write(f"- **策略总收益率**: {self.backtest_results['total_return']:.2f}%\n")
            f.write(f"- **年化收益率**: {self.backtest_results['annual_return']:.2f}%\n")
            f.write(f"- **夏普比率**: {self.backtest_results['sharpe_ratio']:.3f}\n")
            f.write(f"- **最大回撤**: {self.backtest_results['max_drawdown']:.2f}%\n")
            f.write(f"- **风险等级**: {self.risk_analysis['risk_level']}\n\n")
            
            # 基本面分析
            if self.fundamental_analysis:
                f.write("## 基本面分析\n\n")
                f.write("### 公司概况\n\n")
                if 'company_overview' in self.fundamental_analysis:
                    for key, value in self.fundamental_analysis['company_overview'].items():
                        f.write(f"- **{key}**: {value}\n")
                
                f.write("\n### 估值指标\n\n")
                if 'valuation_metrics' in self.fundamental_analysis:
                    for key, value in self.fundamental_analysis['valuation_metrics'].items():
                        f.write(f"- **{key}**: {value}\n")
                f.write("\n")
            
            # 技术分析
            f.write("## 技术分析\n\n")
            f.write("### 价格走势\n\n")
            f.write(f"- **近期趋势**: {'上升' if self.price_df['close'].iloc[-1] > self.price_df['close'].iloc[-20] else '下降'}\n")
            f.write(f"- **当前RSI**: {self.technical_df['RSI'].iloc[-1]:.2f}\n")
            f.write(f"- **MACD状态**: {'看涨' if self.technical_df['MACD'].iloc[-1] > self.technical_df['MACD_signal'].iloc[-1] else '看跌'}\n")
            f.write(f"- **布林带位置**: {'上轨附近' if self.technical_df['close'].iloc[-1] > self.technical_df['BB_upper'].iloc[-1] * 0.95 else '下轨附近' if self.technical_df['close'].iloc[-1] < self.technical_df['BB_lower'].iloc[-1] * 1.05 else '中轨附近'}\n\n")
            
            # 量化策略表现
            f.write("## 量化策略表现\n\n")
            f.write(f"- **策略总收益率**: {self.backtest_results['total_return']:.2f}%\n")
            f.write(f"- **基准收益率**: {self.backtest_results['benchmark_return']:.2f}%\n")
            f.write(f"- **超额收益**: {self.backtest_results['total_return'] - self.backtest_results['benchmark_return']:.2f}%\n")
            f.write(f"- **年化收益率**: {self.backtest_results['annual_return']:.2f}%\n")
            f.write(f"- **夏普比率**: {self.backtest_results['sharpe_ratio']:.3f}\n")
            f.write(f"- **最大回撤**: {self.backtest_results['max_drawdown']:.2f}%\n")
            f.write(f"- **波动率**: {self.backtest_results['volatility']:.2f}%\n")
            f.write(f"- **胜率**: {self.backtest_results['win_rate']:.1f}%\n\n")
            
            # 风险分析
            f.write("## 风险分析\n\n")
            f.write(f"- **年化波动率**: {self.risk_analysis['volatility']:.2f}%\n")
            f.write(f"- **95% VaR**: {self.risk_analysis['var_95']:.2f}%\n")
            f.write(f"- **99% VaR**: {self.risk_analysis['var_99']:.2f}%\n")
            f.write(f"- **最大回撤**: {self.risk_analysis['max_drawdown']:.2f}%\n")
            f.write(f"- **风险等级**: {self.risk_analysis['risk_level']}\n\n")
            
            # 投资建议
            f.write("## 投资建议\n\n")
            if self.backtest_results['total_return'] > self.backtest_results['benchmark_return']:
                f.write("✅ **策略表现优于基准**，可以考虑采用该量化策略\n\n")
            else:
                f.write("❌ **策略表现不如基准**，建议谨慎使用\n\n")
            
            if self.risk_analysis['risk_level'] == "高风险":
                f.write("⚠️ **高风险股票**，建议控制仓位并设置止损\n\n")
            elif self.risk_analysis['risk_level'] == "中等风险":
                f.write("⚡ **中等风险股票**，建议适度配置\n\n")
            else:
                f.write("✅ **低风险股票**，适合稳健投资\n\n")
            
            # 图表说明
            f.write("## 图表说明\n\n")
            f.write("1. **价格和技术指标图**: 展示股价走势、移动平均线、RSI和MACD指标\n")
            f.write("2. **成交量分析图**: 分析成交量变化和价格关系\n")
            f.write("3. **策略回测图**: 展示策略收益、资金曲线、回撤和交易信号\n\n")
            
            f.write("---\n")
            f.write("*本报告由MiniMax Agent量化分析系统生成，仅供参考，不构成投资建议。*\n")
        
        return report_path

class LocalDataManager:
    """本地数据管理类 - 用于演示"""
    
    def __init__(self, stock_code: str, data_dir: str = "data"):
        self.stock_code = stock_code
        self.data_dir = data_dir
        self.price_df = None
        self.info_data = None
        self.financial_data = None
    
    def load_data(self) -> bool:
        """加载本地数据"""
        try:
            # 查找对应的数据文件 - 优先使用现有格式，备选使用标准格式
            possible_names = []
            
            # 对于海欣食品，使用现有文件名
            if self.stock_code == "002702.SZ":
                possible_names = [
                    f"{self.data_dir}/haixin_price.json",
                    f"{self.data_dir}/haixin_info.json", 
                    f"{self.data_dir}/haixin_financial.json"
                ]
            else:
                # 其他股票使用标准命名
                possible_names = [
                    f"{self.data_dir}/{self.stock_code.replace('.', '_')}_price.json",
                    f"{self.data_dir}/{self.stock_code.replace('.', '_')}_info.json",
                    f"{self.data_dir}/{self.stock_code.replace('.', '_')}_financial.json"
                ]
            
            price_file = possible_names[0]
            info_file = possible_names[1]
            financial_file = possible_names[2]
            
            # 加载价格数据
            if os.path.exists(price_file):
                with open(price_file, 'r', encoding='utf-8') as f:
                    price_data = json.load(f)
                
                prices_data = price_data['data']['prices']
                self.price_df = pd.DataFrame(prices_data)
                self.price_df['date'] = pd.to_datetime(self.price_df['date'])
                self.price_df.set_index('date', inplace=True)
                self.price_df.dropna(inplace=True)
            else:
                print(f"⚠️  找不到 {self.stock_code} 的价格数据文件: {price_file}")
                return False
            
            # 加载基本信息
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    self.info_data = json.load(f)['data']
            
            # 加载财务数据
            if os.path.exists(financial_file):
                with open(financial_file, 'r', encoding='utf-8') as f:
                    self.financial_data = json.load(f)['data']
            
            return True
            
        except Exception as e:
            print(f"加载 {self.stock_code} 数据时出错: {str(e)}")
            return False

class MultiStockAnalyzer:
    """多股票分析器"""
    
    def __init__(self, output_dir: str = "analysis_results"):
        self.output_dir = output_dir
        self.results = {}
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("charts", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
    
    def analyze_single_stock(self, stock_code: str, force_refresh: bool = False) -> bool:
        """分析单个股票"""
        try:
            print(f"\n{'='*60}")
            print(f"开始分析股票: {stock_code}")
            print(f"{'='*60}")
            
            # 数据管理 - 使用本地数据
            data_manager = LocalDataManager(stock_code)
            
            if not data_manager.load_data():
                print(f"❌ 无法加载 {stock_code} 的数据")
                return False
            
            if data_manager.price_df is None or data_manager.price_df.empty:
                print(f"❌ 无法获取 {stock_code} 的有效价格数据")
                return False
            
            # 技术分析
            print("1. 进行技术分析...")
            technical_analyzer = TechnicalAnalyzer(data_manager.price_df)
            technical_df = technical_analyzer.calculate_indicators()
            
            # 基本面分析
            print("2. 进行基本面分析...")
            fundamental_analyzer = FundamentalAnalyzer(data_manager.info_data, data_manager.financial_data)
            fundamental_analysis = {}
            
            if data_manager.info_data:
                fundamental_analysis['company_overview'] = fundamental_analyzer.get_company_overview()
                fundamental_analysis['valuation_metrics'] = fundamental_analyzer.get_valuation_metrics()
            
            # 量化策略
            print("3. 运行量化策略...")
            strategy = QuantitativeStrategies(technical_df)
            signals = strategy.combined_strategy()
            
            # 回测
            print("4. 进行策略回测...")
            backtest = BacktestEngine(technical_df)
            backtest_results, backtest_df = backtest.run_backtest(signals)
            technical_df = backtest_df
            
            # 风险管理
            print("5. 进行风险分析...")
            risk_manager = RiskManager(technical_df)
            risk_analysis = risk_manager.risk_assessment()
            
            # 可视化
            print("6. 生成可视化图表...")
            visualizer = VisualizationEngine(technical_df, stock_code)
            visualizer.initial_capital = 100000
            visualizer.plot_price_and_indicators()
            visualizer.plot_volume_analysis()
            visualizer.plot_strategy_performance(backtest_results)
            
            # 生成报告
            print("7. 生成分析报告...")
            report_generator = QuantitativeAnalysisReport(
                stock_code, data_manager.price_df, fundamental_analysis, 
                technical_df, backtest_results, risk_analysis
            )
            report_path = report_generator.generate_report()
            
            # 保存结果
            self.results[stock_code] = {
                'backtest_results': backtest_results,
                'risk_analysis': risk_analysis,
                'report_path': report_path,
                'current_price': data_manager.price_df['close'].iloc[-1]
            }
            
            # 输出结果摘要
            print(f"\n=== {stock_code} 分析结果摘要 ===")
            print(f"当前股价: ¥{data_manager.price_df['close'].iloc[-1]:.2f}")
            print(f"策略总收益率: {backtest_results['total_return']:.2f}%")
            print(f"基准收益率: {backtest_results['benchmark_return']:.2f}%")
            print(f"年化收益率: {backtest_results['annual_return']:.2f}%")
            print(f"夏普比率: {backtest_results['sharpe_ratio']:.3f}")
            print(f"最大回撤: {backtest_results['max_drawdown']:.2f}%")
            print(f"风险等级: {risk_analysis['risk_level']}")
            
            print(f"\n分析完成！")
            print(f"- 技术分析图表: charts/{stock_code.replace('.', '_')}_price_indicators.png")
            print(f"- 成交量分析: charts/{stock_code.replace('.', '_')}_volume_analysis.png") 
            print(f"- 策略回测: charts/{stock_code.replace('.', '_')}_strategy_performance.png")
            print(f"- 详细报告: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"分析 {stock_code} 时出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def analyze_multiple_stocks(self, stock_codes: List[str], force_refresh: bool = False) -> bool:
        """批量分析多个股票"""
        print(f"\n开始批量分析 {len(stock_codes)} 只股票...")
        
        success_count = 0
        failed_stocks = []
        
        for stock_code in stock_codes:
            if self.analyze_single_stock(stock_code, force_refresh):
                success_count += 1
            else:
                failed_stocks.append(stock_code)
        
        # 生成对比报告
        if success_count > 1:
            self.generate_comparison_report(stock_codes, success_count, failed_stocks)
        
        print(f"\n{'='*60}")
        print(f"批量分析完成！成功: {success_count}, 失败: {len(failed_stocks)}")
        if failed_stocks:
            print(f"失败股票: {', '.join(failed_stocks)}")
        print(f"{'='*60}")
        
        return success_count > 0
    
    def generate_comparison_report(self, stock_codes: List[str], success_count: int, failed_stocks: List[str]):
        """生成股票对比报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.output_dir}/stock_comparison_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 多股票量化分析对比报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 分析概览\n\n")
            f.write(f"- **分析股票数**: {len(stock_codes)}\n")
            f.write(f"- **成功分析**: {success_count}\n")
            f.write(f"- **分析失败**: {len(failed_stocks)}\n\n")
            
            if failed_stocks:
                f.write("### 分析失败的股票\n\n")
                for stock in failed_stocks:
                    f.write(f"- {stock}\n")
                f.write("\n")
            
            # 对比表格
            f.write("## 策略表现对比\n\n")
            f.write("| 股票代码 | 当前价格 | 总收益率 | 年化收益率 | 夏普比率 | 最大回撤 | 风险等级 |\n")
            f.write("|---------|---------|---------|-----------|---------|---------|----------|\n")
            
            # 按收益率排序
            sorted_stocks = sorted(
                [(code, results) for code, results in self.results.items()],
                key=lambda x: x[1]['backtest_results']['total_return'],
                reverse=True
            )
            
            for stock_code, results in sorted_stocks:
                backtest = results['backtest_results']
                risk = results['risk_analysis']
                f.write(f"| {stock_code} | ¥{results['current_price']:.2f} | {backtest['total_return']:.2f}% | {backtest['annual_return']:.2f}% | {backtest['sharpe_ratio']:.3f} | {backtest['max_drawdown']:.2f}% | {risk['risk_level']} |\n")
            
            f.write("\n")
            
            # 最佳表现股票
            if sorted_stocks:
                best_stock = sorted_stocks[0]
                f.write("## 最佳表现股票\n\n")
                f.write(f"**{best_stock[0]}**\n")
                f.write(f"- 总收益率: {best_stock[1]['backtest_results']['total_return']:.2f}%\n")
                f.write(f"- 年化收益率: {best_stock[1]['backtest_results']['annual_return']:.2f}%\n")
                f.write(f"- 夏普比率: {best_stock[1]['backtest_results']['sharpe_ratio']:.3f}\n")
                f.write(f"- 风险等级: {best_stock[1]['risk_analysis']['risk_level']}\n\n")
            
            # 风险收益分析
            f.write("## 风险收益分析\n\n")
            f.write("### 收益率分布\n\n")
            returns = [results['backtest_results']['total_return'] for results in self.results.values()]
            f.write(f"- 平均收益率: {np.mean(returns):.2f}%\n")
            f.write(f"- 收益率标准差: {np.std(returns):.2f}%\n")
            f.write(f"- 最高收益率: {max(returns):.2f}%\n")
            f.write(f"- 最低收益率: {min(returns):.2f}%\n\n")
            
            f.write("### 风险分布\n\n")
            risk_levels = {}
            for results in self.results.values():
                level = results['risk_analysis']['risk_level']
                risk_levels[level] = risk_levels.get(level, 0) + 1
            
            for level, count in risk_levels.items():
                f.write(f"- {level}: {count}只股票\n")
            
            f.write("\n---\n")
            f.write("*本报告由MiniMax Agent量化分析系统生成，仅供参考，不构成投资建议。*\n")
        
        print(f"\n📊 对比报告已生成: {report_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='多股票量化分析系统演示版')
    parser.add_argument('--stocks', '-s', nargs='+', help='股票代码列表 (例如: 002702.SZ)')
    parser.add_argument('--file', '-f', help='包含股票代码的文件路径 (每行一个股票代码)')
    parser.add_argument('--output', '-o', default='analysis_results', help='输出目录')
    
    args = parser.parse_args()
    
    # 获取股票代码列表
    stock_codes = []
    
    if args.stocks:
        stock_codes = args.stocks
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r', encoding='utf-8') as f:
                stock_codes = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取股票代码（去掉注释部分）
                        stock_code = line.split('#')[0].strip()
                        if stock_code:
                            stock_codes.append(stock_code)
        else:
            print(f"错误: 文件 {args.file} 不存在")
            return False
    else:
        # 默认示例股票 - 使用现有的海欣食品数据
        stock_codes = ['002702.SZ']
        print("未指定股票代码，使用默认示例: 002702.SZ")
    
    if not stock_codes:
        print("错误: 没有指定要分析的股票代码")
        return False
    
    # 创建分析器并执行分析
    analyzer = MultiStockAnalyzer(args.output)
    
    if len(stock_codes) == 1:
        return analyzer.analyze_single_stock(stock_codes[0])
    else:
        return analyzer.analyze_multiple_stocks(stock_codes)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 分析完成！")
    else:
        print("\n❌ 分析失败！")
        sys.exit(1)