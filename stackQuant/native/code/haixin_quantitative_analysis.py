#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海欣食品股票量化分析系统
综合技术分析、基本面分析、量化策略和风险管理
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
# import talib  # 使用纯Python实现技术指标

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
    
    plt.rcParams["axes.unicode_minus"] = False

class StockDataProcessor:
    """股票数据处理器"""
    
    def __init__(self, price_data_file: str, info_data_file: str, financial_data_file: str):
        self.price_data_file = price_data_file
        self.info_data_file = info_data_file
        self.financial_data_file = financial_data_file
        self.price_df = None
        self.info_data = None
        self.financial_data = None
        
    def load_data(self):
        """加载所有数据"""
        # 加载价格数据
        with open(self.price_data_file, 'r', encoding='utf-8') as f:
            price_data = json.load(f)
        
        # 转换为DataFrame
        prices_data = price_data['data']['prices']
        
        self.price_df = pd.DataFrame(prices_data)
        
        # 转换日期
        self.price_df['date'] = pd.to_datetime(self.price_df['date'])
        self.price_df.set_index('date', inplace=True)
        self.price_df.dropna(inplace=True)
        
        # 加载基本信息
        with open(self.info_data_file, 'r', encoding='utf-8') as f:
            self.info_data = json.load(f)['data']
        
        # 加载财务数据
        with open(self.financial_data_file, 'r', encoding='utf-8') as f:
            self.financial_data = json.load(f)['data']
        
        return self

class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self, price_df: pd.DataFrame):
        self.price_df = price_df.copy()
        
    def calculate_sma(self, window: int = 20) -> pd.Series:
        """简单移动平均线"""
        return self.price_df['close'].rolling(window=window).mean()
    
    def calculate_ema(self, window: int = 20) -> pd.Series:
        """指数移动平均线"""
        return self.price_df['close'].ewm(span=window).mean()
    
    def calculate_rsi(self, window: int = 14) -> pd.Series:
        """相对强弱指数"""
        delta = self.price_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD指标"""
        ema_fast = self.price_df['close'].ewm(span=fast).mean()
        ema_slow = self.price_df['close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, window: int = 20, num_std: float = 2) -> Dict[str, pd.Series]:
        """布林带"""
        sma = self.calculate_sma(window)
        std = self.price_df['close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    def calculate_stochastic(self, k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """随机指标"""
        low_min = self.price_df['low'].rolling(window=k_window).min()
        high_max = self.price_df['high'].rolling(window=k_window).max()
        k_percent = 100 * ((self.price_df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    def calculate_all_indicators(self) -> pd.DataFrame:
        """计算所有技术指标"""
        df = self.price_df.copy()
        
        # 移动平均线
        df['sma_5'] = self.calculate_sma(5)
        df['sma_10'] = self.calculate_sma(10)
        df['sma_20'] = self.calculate_sma(20)
        df['sma_60'] = self.calculate_sma(60)
        df['ema_12'] = self.calculate_ema(12)
        df['ema_26'] = self.calculate_ema(26)
        
        # RSI
        df['rsi'] = self.calculate_rsi()
        
        # MACD
        macd_data = self.calculate_macd()
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # 布林带
        bb_data = self.calculate_bollinger_bands()
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # 随机指标
        stoch_data = self.calculate_stochastic()
        df['stoch_k'] = stoch_data['k']
        df['stoch_d'] = stoch_data['d']
        
        # 价格变化率
        df['price_change'] = df['close'].pct_change()
        df['price_change_5d'] = df['close'].pct_change(5)
        df['price_change_20d'] = df['close'].pct_change(20)
        
        # 成交量指标
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # 波动率
        df['volatility'] = df['price_change'].rolling(window=20).std()
        
        return df

class FundamentalAnalyzer:
    """基本面分析器"""
    
    def __init__(self, info_data: Dict, financial_data: Dict):
        self.info_data = info_data
        self.financial_data = financial_data
    
    def analyze_financial_health(self) -> Dict:
        """分析财务健康状况"""
        metrics = self.financial_data.get('financial_metrics', {})
        profitability = self.financial_data.get('profitability', {})
        growth = self.financial_data.get('growth', {})
        returns = self.financial_data.get('returns', {})
        
        analysis = {
            'liquidity': {
                'current_ratio': metrics.get('current_ratio', 0),
                'quick_ratio': metrics.get('quick_ratio', 0),
                'score': '良好' if metrics.get('current_ratio', 0) > 1.5 else '一般' if metrics.get('current_ratio', 0) > 1.0 else '较差'
            },
            'leverage': {
                'debt_to_equity': metrics.get('debt_to_equity', 0),
                'score': '良好' if metrics.get('debt_to_equity', 0) < 50 else '一般' if metrics.get('debt_to_equity', 0) < 100 else '较高'
            },
            'profitability': {
                'gross_margin': profitability.get('gross_margin', 0),
                'operating_margin': profitability.get('operating_margin', 0),
                'profit_margin': profitability.get('profit_margin', 0),
                'score': '良好' if profitability.get('profit_margin', 0) > 0.05 else '一般' if profitability.get('profit_margin', 0) > 0 else '亏损'
            },
            'growth': {
                'revenue_growth': growth.get('revenue_growth', 0),
                'score': '良好' if growth.get('revenue_growth', 0) > 0.1 else '一般' if growth.get('revenue_growth', 0) > 0 else '下降'
            },
            'efficiency': {
                'roe': returns.get('return_on_equity', 0),
                'roa': returns.get('return_on_assets', 0),
                'score': '良好' if returns.get('return_on_equity', 0) > 0.1 else '一般' if returns.get('return_on_equity', 0) > 0 else '较低'
            }
        }
        
        return analysis
    
    def get_valuation_metrics(self) -> Dict:
        """获取估值指标"""
        info = self.info_data
        financial = self.financial_data
        
        return {
            'market_cap': info.get('market_cap', 0),
            'pe_ratio': info.get('pe_ratio', 0),
            'forward_pe': info.get('forward_pe', 0),
            'dividend_yield': info.get('dividend_yield', 0),
            'beta': info.get('beta', 0),
            'price_to_book': financial.get('price', {}).get('current', 0) / (financial.get('financial_metrics', {}).get('total_cash', 0) / info.get('market_cap', 1)) if info.get('market_cap', 0) > 0 else 0
        }

class QuantitativeStrategies:
    """量化策略"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def mean_reversion_strategy(self) -> pd.Series:
        """均值回归策略"""
        # 基于RSI的均值回归
        signals = pd.Series(0, index=self.df.index)
        signals[self.df['rsi'] < 30] = 1  # 超卖买入
        signals[self.df['rsi'] > 70] = -1  # 超买卖出
        return signals
    
    def momentum_strategy(self) -> pd.Series:
        """动量策略"""
        # 基于MACD和价格动量
        signals = pd.Series(0, index=self.df.index)
        
        # MACD金叉死叉
        macd_golden_cross = (self.df['macd'] > self.df['macd_signal']) & (self.df['macd'].shift(1) <= self.df['macd_signal'].shift(1))
        macd_death_cross = (self.df['macd'] < self.df['macd_signal']) & (self.df['macd'].shift(1) >= self.df['macd_signal'].shift(1))
        
        signals[macd_golden_cross] = 1
        signals[macd_death_cross] = -1
        
        return signals
    
    def bollinger_bands_strategy(self) -> pd.Series:
        """布林带策略"""
        signals = pd.Series(0, index=self.df.index)
        
        # 价格触及下轨买入，触及上轨卖出
        signals[self.df['close'] < self.df['bb_lower']] = 1
        signals[self.df['close'] > self.df['bb_upper']] = -1
        
        return signals
    
    def dual_moving_average_strategy(self, short_window: int = 5, long_window: int = 20) -> pd.Series:
        """双均线策略"""
        signals = pd.Series(0, index=self.df.index)
        
        short_ma = self.df['close'].rolling(window=short_window).mean()
        long_ma = self.df['close'].rolling(window=long_window).mean()
        
        # 短期均线上穿长期均线买入，下穿卖出
        golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        
        signals[golden_cross] = 1
        signals[death_cross] = -1
        
        return signals
    
    def combined_strategy(self) -> pd.Series:
        """综合策略"""
        mean_rev = self.mean_reversion_strategy()
        momentum = self.momentum_strategy()
        bollinger = self.bollinger_bands_strategy()
        dual_ma = self.dual_moving_average_strategy()
        
        # 综合信号
        combined = mean_rev + momentum + bollinger + dual_ma
        
        # 归一化到-1, 0, 1
        signals = pd.Series(0, index=self.df.index)
        signals[combined >= 2] = 1
        signals[combined <= -2] = -1
        
        return signals

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, df: pd.DataFrame, initial_capital: float = 100000):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.portfolio = {
            'cash': initial_capital,
            'shares': 0,
            'value': initial_capital,
            'returns': []
        }
    
    def run_backtest(self, signals: pd.Series) -> Dict:
        """运行回测"""
        portfolio_value = []
        cash = self.initial_capital
        shares = 0
        
        for i, (date, signal) in enumerate(signals.items()):
            current_price = self.df.loc[date, 'close']
            
            if signal == 1 and cash > current_price:  # 买入信号
                shares_to_buy = int(cash * 0.95 / current_price)  # 95%资金买入
                if shares_to_buy > 0:
                    shares += shares_to_buy
                    cash -= shares_to_buy * current_price
            
            elif signal == -1 and shares > 0:  # 卖出信号
                cash += shares * current_price
                shares = 0
            
            # 计算组合价值
            total_value = cash + shares * current_price
            portfolio_value.append(total_value)
            
            # 计算收益率
            if i > 0:
                daily_return = (total_value - portfolio_value[i-1]) / portfolio_value[i-1]
                self.portfolio['returns'].append(daily_return)
        
        # 计算回测结果
        self.df['portfolio_value'] = portfolio_value
        self.df['strategy_returns'] = self.df['portfolio_value'].pct_change()
        
        # 基准收益（买入持有）
        self.df['benchmark_returns'] = (self.df['close'] / self.df['close'].iloc[0] - 1) * self.initial_capital
        
        return self.calculate_performance_metrics(), self.df
    
    def calculate_performance_metrics(self) -> Dict:
        """计算绩效指标"""
        strategy_returns = self.df['strategy_returns'].dropna()
        benchmark_returns = self.df['close'].pct_change().dropna()
        
        # 总收益率
        total_return = (self.df['portfolio_value'].iloc[-1] / self.initial_capital - 1) * 100
        benchmark_return = (self.df['close'].iloc[-1] / self.df['close'].iloc[0] - 1) * 100
        
        # 年化收益率
        days = len(self.df)
        annual_return = ((self.df['portfolio_value'].iloc[-1] / self.initial_capital) ** (252/days) - 1) * 100
        benchmark_annual = ((self.df['close'].iloc[-1] / self.df['close'].iloc[0]) ** (252/days) - 1) * 100
        
        # 最大回撤
        rolling_max = self.df['portfolio_value'].expanding().max()
        drawdown = (self.df['portfolio_value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # 夏普比率
        risk_free_rate = 0.03  # 假设无风险利率3%
        excess_returns = strategy_returns.mean() * 252 - risk_free_rate
        sharpe_ratio = excess_returns / (strategy_returns.std() * np.sqrt(252))
        
        # 胜率
        win_rate = (strategy_returns > 0).mean() * 100
        
        return {
            'total_return': total_return,
            'benchmark_return': benchmark_return,
            'annual_return': annual_return,
            'benchmark_annual': benchmark_annual,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'final_value': self.df['portfolio_value'].iloc[-1]
        }

class RiskManager:
    """风险管理"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def calculate_var(self, confidence_level: float = 0.05, window: int = 252) -> float:
        """计算风险价值(VaR)"""
        returns = self.df['close'].pct_change().dropna()
        var = np.percentile(returns, confidence_level * 100)
        return var * 100
    
    def calculate_cvar(self, confidence_level: float = 0.05, window: int = 252) -> float:
        """计算条件风险价值(CVaR)"""
        returns = self.df['close'].pct_change().dropna()
        var = np.percentile(returns, confidence_level * 100)
        cvar = returns[returns <= var].mean()
        return cvar * 100
    
    def calculate_beta(self, market_returns: pd.Series) -> float:
        """计算Beta系数"""
        stock_returns = self.df['close'].pct_change().dropna()
        aligned_returns = stock_returns.align(market_returns, join='inner')[0]
        aligned_market = stock_returns.align(market_returns, join='inner')[1]
        
        if len(aligned_returns) > 1:
            covariance = np.cov(aligned_returns, aligned_market)[0, 1]
            market_variance = np.var(aligned_market)
            beta = covariance / market_variance if market_variance != 0 else 0
            return beta
        return 0
    
    def risk_assessment(self) -> Dict:
        """风险评估"""
        returns = self.df['close'].pct_change().dropna()
        
        # 波动率
        volatility = returns.std() * np.sqrt(252) * 100
        
        # VaR和CVaR
        var_5 = self.calculate_var(0.05)
        cvar_5 = self.calculate_cvar(0.05)
        
        # 最大回撤
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        return {
            'volatility': volatility,
            'var_5': var_5,
            'cvar_5': cvar_5,
            'max_drawdown': max_drawdown,
            'risk_level': '高' if volatility > 30 else '中' if volatility > 15 else '低'
        }

class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        setup_matplotlib_for_plotting()
    
    def plot_price_and_indicators(self, save_path: str = 'charts/price_indicators.png'):
        """绘制价格和技术指标"""
        fig, axes = plt.subplots(4, 1, figsize=(15, 20))
        
        # 价格和移动平均线
        axes[0].plot(self.df.index, self.df['close'], label='收盘价', linewidth=2)
        axes[0].plot(self.df.index, self.df['sma_5'], label='MA5', alpha=0.7)
        axes[0].plot(self.df.index, self.df['sma_20'], label='MA20', alpha=0.7)
        axes[0].plot(self.df.index, self.df['sma_60'], label='MA60', alpha=0.7)
        axes[0].set_title('海欣食品股价走势与移动平均线', fontsize=16, fontweight='bold')
        axes[0].set_ylabel('价格 (元)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 布林带
        axes[1].plot(self.df.index, self.df['close'], label='收盘价', linewidth=2)
        axes[1].plot(self.df.index, self.df['bb_upper'], label='布林上轨', alpha=0.7)
        axes[1].plot(self.df.index, self.df['bb_middle'], label='布林中轨', alpha=0.7)
        axes[1].plot(self.df.index, self.df['bb_lower'], label='布林下轨', alpha=0.7)
        axes[1].fill_between(self.df.index, self.df['bb_upper'], self.df['bb_lower'], alpha=0.2)
        axes[1].set_title('布林带指标', fontsize=14)
        axes[1].set_ylabel('价格 (元)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # MACD
        axes[2].plot(self.df.index, self.df['macd'], label='MACD', linewidth=2)
        axes[2].plot(self.df.index, self.df['macd_signal'], label='信号线', linewidth=2)
        axes[2].bar(self.df.index, self.df['macd_histogram'], label='MACD柱', alpha=0.6)
        axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        axes[2].set_title('MACD指标', fontsize=14)
        axes[2].set_ylabel('MACD')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # RSI和随机指标
        axes[3].plot(self.df.index, self.df['rsi'], label='RSI', linewidth=2, color='purple')
        axes[3].axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线')
        axes[3].axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线')
        axes[3].set_title('RSI指标', fontsize=14)
        axes[3].set_ylabel('RSI')
        axes[3].set_xlabel('日期')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_volume_analysis(self, save_path: str = 'charts/volume_analysis.png'):
        """绘制成交量分析"""
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # 成交量
        axes[0].bar(self.df.index, self.df['volume'], alpha=0.7, color='blue')
        axes[0].plot(self.df.index, self.df['volume_sma'], label='成交量均线', color='red', linewidth=2)
        axes[0].set_title('成交量分析', fontsize=16, fontweight='bold')
        axes[0].set_ylabel('成交量')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 价格与成交量关系
        colors = ['red' if close >= open else 'green' for close, open in zip(self.df['close'], self.df['open'])]
        axes[1].scatter(self.df['volume'], self.df['close'], c=colors, alpha=0.6)
        axes[1].set_title('成交量与价格关系', fontsize=14)
        axes[1].set_xlabel('成交量')
        axes[1].set_ylabel('价格 (元)')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def plot_strategy_performance(self, backtest_results: Dict, save_path: str = 'charts/strategy_performance.png'):
        """绘制策略回测结果"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 组合价值走势
        axes[0,0].plot(self.df.index, self.df['portfolio_value'], label='策略组合', linewidth=2, color='blue')
        axes[0,0].plot(self.df.index, self.df['benchmark_returns'] + self.initial_capital, label='基准(买入持有)', linewidth=2, color='red')
        axes[0,0].set_title('组合价值走势', fontsize=14, fontweight='bold')
        axes[0,0].set_ylabel('价值 (元)')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # 累积收益率
        strategy_cumret = (self.df['portfolio_value'] / self.initial_capital - 1) * 100
        benchmark_cumret = (self.df['close'] / self.df['close'].iloc[0] - 1) * 100
        axes[0,1].plot(self.df.index, strategy_cumret, label='策略收益率', linewidth=2, color='blue')
        axes[0,1].plot(self.df.index, benchmark_cumret, label='基准收益率', linewidth=2, color='red')
        axes[0,1].set_title('累积收益率对比', fontsize=14)
        axes[0,1].set_ylabel('收益率 (%)')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
        
        # 回撤分析
        rolling_max = self.df['portfolio_value'].expanding().max()
        drawdown = (self.df['portfolio_value'] - rolling_max) / rolling_max * 100
        axes[1,0].fill_between(self.df.index, drawdown, 0, alpha=0.7, color='red')
        axes[1,0].set_title('策略回撤分析', fontsize=14)
        axes[1,0].set_ylabel('回撤 (%)')
        axes[1,0].grid(True, alpha=0.3)
        
        # 绩效指标
        metrics = ['总收益率', '年化收益率', '夏普比率', '胜率', '最大回撤']
        values = [
            backtest_results['total_return'],
            backtest_results['annual_return'],
            backtest_results['sharpe_ratio'] * 10,  # 缩放以便显示
            backtest_results['win_rate'],
            abs(backtest_results['max_drawdown'])
        ]
        
        colors = ['green' if v > 0 else 'red' for v in values]
        bars = axes[1,1].bar(metrics, values, color=colors, alpha=0.7)
        axes[1,1].set_title('策略绩效指标', fontsize=14)
        axes[1,1].set_ylabel('数值')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                          f'{value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path

class QuantitativeAnalysisReport:
    """量化分析报告生成器"""
    
    def __init__(self, symbol: str, price_df: pd.DataFrame, fundamental_analysis: Dict, 
                 technical_analysis: pd.DataFrame, backtest_results: Dict, risk_analysis: Dict):
        self.symbol = symbol
        self.price_df = price_df
        self.fundamental_analysis = fundamental_analysis
        self.technical_analysis = technical_analysis
        self.backtest_results = backtest_results
        self.risk_analysis = risk_analysis
    
    def generate_report(self, save_path: str = 'docs/haixin_quantitative_report.md'):
        """生成分析报告"""
        report = f"""# 海欣食品(002702.SZ)量化分析报告

## 执行摘要

本报告对海欣食品(002702.SZ)进行了全面的量化分析，包括技术分析、基本面分析、量化策略回测和风险管理。

**分析期间**: {self.price_df.index[0].strftime('%Y-%m-%d')} 至 {self.price_df.index[-1].strftime('%Y-%m-%d')}

**当前股价**: ¥{self.price_df['close'].iloc[-1]:.2f}

## 1. 技术分析

### 1.1 价格趋势分析
- **当前价格**: ¥{self.price_df['close'].iloc[-1]:.2f}
- **52周最高**: ¥{self.price_df['close'].max():.2f}
- **52周最低**: ¥{self.price_df['close'].min():.2f}
- **价格波动率**: {self.risk_analysis['volatility']:.2f}%

### 1.2 技术指标状态
- **RSI**: {self.technical_analysis['rsi'].iloc[-1]:.2f}
  - 状态: {'超买' if self.technical_analysis['rsi'].iloc[-1] > 70 else '超卖' if self.technical_analysis['rsi'].iloc[-1] < 30 else '正常'}
- **MACD**: {self.technical_analysis['macd'].iloc[-1]:.4f}
  - 信号: {'买入' if self.technical_analysis['macd'].iloc[-1] > self.technical_analysis['macd_signal'].iloc[-1] else '卖出'}
- **布林带位置**: {self.technical_analysis['bb_position'].iloc[-1]:.2%}
  - 状态: {'接近上轨' if self.technical_analysis['bb_position'].iloc[-1] > 0.8 else '接近下轨' if self.technical_analysis['bb_position'].iloc[-1] < 0.2 else '中性'}

### 1.3 移动平均线状态
- MA5: ¥{self.technical_analysis['sma_5'].iloc[-1]:.2f}
- MA20: ¥{self.technical_analysis['sma_20'].iloc[-1]:.2f}
- MA60: ¥{self.technical_analysis['sma_60'].iloc[-1]:.2f}

## 2. 基本面分析

### 2.1 财务健康状况
- **流动性**: {self.fundamental_analysis['liquidity']['score']}
  - 流动比率: {self.fundamental_analysis['liquidity']['current_ratio']:.2f}
  - 速动比率: {self.fundamental_analysis['liquidity']['quick_ratio']:.2f}

- **杠杆水平**: {self.fundamental_analysis['leverage']['score']}
  - 资产负债率: {self.fundamental_analysis['leverage']['debt_to_equity']:.2f}%

- **盈利能力**: {self.fundamental_analysis['profitability']['score']}
  - 毛利率: {self.fundamental_analysis['profitability']['gross_margin']*100:.2f}%
  - 营业利润率: {self.fundamental_analysis['profitability']['operating_margin']*100:.2f}%
  - 净利润率: {self.fundamental_analysis['profitability']['profit_margin']*100:.2f}%

- **成长性**: {self.fundamental_analysis['growth']['score']}
  - 营收增长率: {self.fundamental_analysis['growth']['revenue_growth']*100:.2f}%

- **运营效率**: {self.fundamental_analysis['efficiency']['score']}
  - ROE: {self.fundamental_analysis['efficiency']['roe']*100:.2f}%
  - ROA: {self.fundamental_analysis['efficiency']['roa']*100:.2f}%

### 2.2 估值指标
- 市值: ¥{self.fundamental_analysis.get('market_cap', 0)/100000000:.2f}亿
- P/E比率: {self.fundamental_analysis.get('pe_ratio', 0):.2f}
- 股息收益率: {self.fundamental_analysis.get('dividend_yield', 0)*100:.2f}%
- Beta系数: {self.fundamental_analysis.get('beta', 0):.2f}

## 3. 量化策略回测

### 3.1 策略概述
本分析采用多因子量化策略，结合以下策略：
- 均值回归策略（基于RSI）
- 动量策略（基于MACD）
- 布林带策略
- 双均线策略

### 3.2 回测结果
- **初始资金**: ¥100,000
- **最终价值**: ¥{self.backtest_results['final_value']:,.2f}
- **总收益率**: {self.backtest_results['total_return']:.2f}%
- **年化收益率**: {self.backtest_results['annual_return']:.2f}%
- **基准收益率**: {self.backtest_results['benchmark_return']:.2f}%
- **超额收益**: {self.backtest_results['total_return'] - self.backtest_results['benchmark_return']:.2f}%

### 3.3 风险调整收益
- **夏普比率**: {self.backtest_results['sharpe_ratio']:.3f}
- **最大回撤**: {self.backtest_results['max_drawdown']:.2f}%
- **胜率**: {self.backtest_results['win_rate']:.1f}%

## 4. 风险分析

### 4.1 风险指标
- **波动率**: {self.risk_analysis['volatility']:.2f}%
- **VaR (5%)**: {self.risk_analysis['var_5']:.2f}%
- **CVaR (5%)**: {self.risk_analysis['cvar_5']:.2f}%
- **最大回撤**: {self.risk_analysis['max_drawdown']:.2f}%
- **风险等级**: {self.risk_analysis['risk_level']}

### 4.2 风险评估
{'高风险' if self.risk_analysis['risk_level'] == '高' else '中等风险' if self.risk_analysis['risk_level'] == '中' else '低风险'}投资标的，适合{'激进' if self.risk_analysis['risk_level'] == '高' else '稳健' if self.risk_analysis['risk_level'] == '中' else '保守'}型投资者。

## 5. 投资建议

### 5.1 技术面建议
"""
        
        # 技术面建议
        latest_rsi = self.technical_analysis['rsi'].iloc[-1]
        latest_macd = self.technical_analysis['macd'].iloc[-1]
        latest_signal = self.technical_analysis['macd_signal'].iloc[-1]
        latest_price = self.price_df['close'].iloc[-1]
        
        if latest_rsi < 30:
            report += "- RSI显示超卖状态，可能存在反弹机会\n"
        elif latest_rsi > 70:
            report += "- RSI显示超买状态，建议谨慎\n"
        else:
            report += "- RSI处于正常区间\n"
            
        if latest_macd > latest_signal:
            report += "- MACD呈现买入信号\n"
        else:
            report += "- MACD呈现卖出信号\n"
        
        report += f"""
### 5.2 基本面建议
- 财务状况: {self.fundamental_analysis['profitability']['score']}
- 建议关注公司盈利能力改善情况
- 建议关注现金流状况

### 5.3 风险管理建议
- 建议设置止损位: ¥{latest_price * 0.9:.2f} (10%止损)
- 建议分批建仓，控制仓位
- 密切关注市场情绪和行业政策变化

## 6. 免责声明

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
投资者应根据自身风险承受能力做出投资决策。

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: Yahoo Finance*
"""
        
        # 保存报告
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return save_path

def main():
    """主函数"""
    print("=== 海欣食品股票量化分析系统 ===\n")
    
    # 创建必要的目录
    import os
    os.makedirs('charts', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    try:
        # 1. 数据加载和处理
        print("1. 加载数据...")
        processor = StockDataProcessor(
            '/workspace/data/haixin_price.json',
            '/workspace/data/haixin_info.json', 
            '/workspace/data/haixin_financial.json'
        )
        processor.load_data()
        
        # 2. 技术分析
        print("2. 进行技术分析...")
        technical_analyzer = TechnicalAnalyzer(processor.price_df)
        technical_df = technical_analyzer.calculate_all_indicators()
        
        # 3. 基本面分析
        print("3. 进行基本面分析...")
        fundamental_analyzer = FundamentalAnalyzer(processor.info_data, processor.financial_data)
        fundamental_analysis = fundamental_analyzer.analyze_financial_health()
        valuation_metrics = fundamental_analyzer.get_valuation_metrics()
        fundamental_analysis.update(valuation_metrics)
        
        # 4. 量化策略
        print("4. 运行量化策略...")
        strategy = QuantitativeStrategies(technical_df)
        signals = strategy.combined_strategy()
        
        # 5. 回测
        print("5. 进行策略回测...")
        backtest = BacktestEngine(technical_df)
        backtest_results, backtest_df = backtest.run_backtest(signals)
        technical_df = backtest_df  # 使用包含回测结果的DataFrame
        
        # 6. 风险管理
        print("6. 进行风险分析...")
        risk_manager = RiskManager(technical_df)
        risk_analysis = risk_manager.risk_assessment()
        
        # 7. 可视化
        print("7. 生成可视化图表...")
        visualizer = VisualizationEngine(technical_df)
        visualizer.initial_capital = 100000  # 设置初始资金
        visualizer.plot_price_and_indicators()
        visualizer.plot_volume_analysis()
        visualizer.plot_strategy_performance(backtest_results)
        
        # 8. 生成报告
        print("8. 生成分析报告...")
        report_generator = QuantitativeAnalysisReport(
            '002702.SZ', processor.price_df, fundamental_analysis, 
            technical_df, backtest_results, risk_analysis
        )
        report_path = report_generator.generate_report()
        
        # 9. 输出结果摘要
        print("\n=== 分析结果摘要 ===")
        print(f"当前股价: ¥{processor.price_df['close'].iloc[-1]:.2f}")
        print(f"策略总收益率: {backtest_results['total_return']:.2f}%")
        print(f"基准收益率: {backtest_results['benchmark_return']:.2f}%")
        print(f"年化收益率: {backtest_results['annual_return']:.2f}%")
        print(f"夏普比率: {backtest_results['sharpe_ratio']:.3f}")
        print(f"最大回撤: {backtest_results['max_drawdown']:.2f}%")
        print(f"风险等级: {risk_analysis['risk_level']}")
        
        print(f"\n分析完成！")
        print(f"- 技术分析图表: charts/price_indicators.png")
        print(f"- 成交量分析: charts/volume_analysis.png") 
        print(f"- 策略回测: charts/strategy_performance.png")
        print(f"- 详细报告: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()