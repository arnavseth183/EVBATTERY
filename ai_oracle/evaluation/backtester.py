"""
Backtester Module
=================
Institution-grade vectorized backtesting engine
Supports:
- Long/Short strategies
- Transaction cost modeling
- Slippage modeling
- Portfolio tracking
- Performance metrics integration
- Risk hooks
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class BacktestConfig:
    initial_capital: float = 1_000_000
    transaction_cost: float = 0.001  # 0.1%
    slippage: float = 0.0005
    allow_short: bool = True
    risk_free_rate: float = 0.05


class Backtester:
    def __init__(self, price_data: pd.DataFrame,
                 signals: pd.Series,
                 config: Optional[BacktestConfig] = None):

        self.price_data = price_data.copy()
        self.signals = signals.copy()
        self.config = config or BacktestConfig()

        self.results = pd.DataFrame(index=price_data.index)

    def _apply_slippage(self, returns: pd.Series) -> pd.Series:
        return returns - self.config.slippage

    def _apply_transaction_cost(self, trades: pd.Series) -> pd.Series:
        return trades * self.config.transaction_cost

    def run(self) -> pd.DataFrame:
        logger.info("Starting backtest execution")

        returns = self.price_data["close"].pct_change().fillna(0)

        positions = self.signals.shift(1).fillna(0)

        if not self.config.allow_short:
            positions = positions.clip(lower=0)

        strategy_returns = positions * returns
        strategy_returns = self._apply_slippage(strategy_returns)

        trades = positions.diff().abs().fillna(0)
        costs = self._apply_transaction_cost(trades)

        net_returns = strategy_returns - costs

        equity_curve = (1 + net_returns).cumprod() * self.config.initial_capital

        self.results["returns"] = net_returns
        self.results["equity"] = equity_curve
        self.results["positions"] = positions

        logger.info("Backtest completed successfully")
        return self.results

    def calculate_drawdown(self) -> pd.Series:
        equity = self.results["equity"]
        peak = equity.cummax()
        drawdown = (equity - peak) / peak
        return drawdown

    def calculate_sharpe_ratio(self):
        """
        Calculate the Sharpe Ratio.
        """
        avg_return = self.results["returns"].mean()
        volatility = self.results["returns"].std()
        sharpe_ratio = (avg_return - self.config.risk_free_rate / 252) / volatility
        return sharpe_ratio

    def calculate_sortino_ratio(self):
        """
        Calculate the Sortino Ratio.
        """
        downside_returns = self.results["returns"][self.results["returns"] < 0]
        downside_volatility = downside_returns.std()
        avg_return = self.results["returns"].mean()
        sortino_ratio = (avg_return - self.config.risk_free_rate / 252) / downside_volatility
        return sortino_ratio

    def summary(self) -> Dict[str, float]:
        total_return = self.results["equity"].iloc[-1] / self.config.initial_capital - 1
        max_drawdown = self.calculate_drawdown().min()
        volatility = self.results["returns"].std() * np.sqrt(252)

        return {
            "Total Return": total_return,
            "Max Drawdown": max_drawdown,
            "Volatility": volatility
        }

    def extended_summary(self):
        """
        Provide an extended summary with additional metrics.
        """
        summary = self.summary()
        summary.update({
            "Sharpe Ratio": self.calculate_sharpe_ratio(),
            "Sortino Ratio": self.calculate_sortino_ratio(),
        })
        return summary