"""Módulo de Backtesting Engine - Valida estrategia con datos históricos"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Motor de backtesting para validar estrategias de trading"""

    def __init__(self, symbol: str, timeframe: int, initial_balance: float = 10000):
        """
        Inicializar motor de backtesting
        
        Args:
            symbol: Símbolo a backtestear (ej: EU50)
            timeframe: Timeframe en minutos
            initial_balance: Balance inicial para el backtest
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Histórico de trades
        self.trades = []
        self.equity_history = [initial_balance]
        
        logger.info(f"BacktestEngine inicializado - Symbol: {symbol}, Timeframe: {timeframe}m, Balance: ${initial_balance}")

    def backtest(self, prices: np.ndarray, strategy_func, lot_size: float = 0.1, 
                 stop_loss_pips: float = 50, take_profit_pips: float = 100) -> Dict:
        """
        Ejecutar backtest completo
        
        Args:
            prices: Array de precios de cierre
            strategy_func: Función de estrategia que retorna señal (BUY/SELL/None)
            lot_size: Tamaño del lote
            stop_loss_pips: Stop loss en pips
            take_profit_pips: Take profit en pips
            
        Returns:
            dict: Resultados del backtest
        """
        logger.info(f"Iniciando backtest con {len(prices)} barras")
        
        self.trades = []
        self.equity_history = [self.initial_balance]
        self.current_balance = self.initial_balance
        
        position = None  # None, 'BUY', 'SELL'
        entry_price = None
        entry_index = None
        
        pip_value = 0.0001  # Valor de 1 pip (ajustar según símbolo)
        
        # Iterar sobre todas las barras
        for i in range(1, len(prices)):
            current_price = prices[i]
            
            # Si hay posición abierta, verificar SL/TP
            if position is not None:
                if position == "BUY":
                    # Verificar Stop Loss
                    if current_price <= entry_price - (stop_loss_pips * pip_value):
                        profit = (entry_price - current_price) * lot_size / pip_value
                        self._close_trade(i, current_price, entry_price, position, profit, "SL")
                        position = None
                    # Verificar Take Profit
                    elif current_price >= entry_price + (take_profit_pips * pip_value):
                        profit = (current_price - entry_price) * lot_size / pip_value
                        self._close_trade(i, current_price, entry_price, position, profit, "TP")
                        position = None
                
                elif position == "SELL":
                    # Verificar Stop Loss
                    if current_price >= entry_price + (stop_loss_pips * pip_value):
                        profit = (entry_price - current_price) * lot_size / pip_value
                        self._close_trade(i, current_price, entry_price, position, profit, "SL")
                        position = None
                    # Verificar Take Profit
                    elif current_price <= entry_price - (take_profit_pips * pip_value):
                        profit = (current_price - entry_price) * lot_size / pip_value
                        self._close_trade(i, current_price, entry_price, position, profit, "TP")
                        position = None
            
            # Generar señal si no hay posición abierta
            if position is None:
                signal = strategy_func(prices[:i+1])
                
                if signal == "BUY":
                    position = "BUY"
                    entry_price = current_price
                    entry_index = i
                    logger.debug(f"Señal BUY en barra {i}, precio: {current_price:.5f}")
                
                elif signal == "SELL":
                    position = "SELL"
                    entry_price = current_price
                    entry_index = i
                    logger.debug(f"Señal SELL en barra {i}, precio: {current_price:.5f}")
            
            # Registrar equity
            self.equity_history.append(self.current_balance)
        
        # Si hay posición abierta al final, cerrarla
        if position is not None:
            final_price = prices[-1]
            if position == "BUY":
                profit = (final_price - entry_price) * lot_size / pip_value
            else:
                profit = (entry_price - final_price) * lot_size / pip_value
            self._close_trade(len(prices) - 1, final_price, entry_price, position, profit, "END")
        
        # Calcular métricas
        results = self._calculate_metrics()
        return results

    def _close_trade(self, bar_index: int, close_price: float, entry_price: float, 
                     position_type: str, profit: float, reason: str):
        """
        Registrar cierre de trade
        
        Args:
            bar_index: Índice de la barra
            close_price: Precio de cierre
            entry_price: Precio de entrada
            position_type: Tipo de posición (BUY/SELL)
            profit: Ganancia/pérdida en dinero
            reason: Razón del cierre (TP/SL/END)
        """
        trade = {
            "entry_index": bar_index - 1,
            "close_index": bar_index,
            "entry_price": entry_price,
            "close_price": close_price,
            "type": position_type,
            "profit": profit,
            "reason": reason
        }
        
        self.trades.append(trade)
        self.current_balance += profit
        logger.debug(f"Trade cerrado - Tipo: {position_type}, Ganancia: ${profit:.2f}, Razón: {reason}")

    def _calculate_metrics(self) -> Dict:
        """
        Calcular métricas de performance
        
        Returns:
            dict: Métricas del backtest
        """
        if len(self.trades) == 0:
            logger.warning("No hay trades para calcular métricas")
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_profit": 0,
                "profit_factor": 0,
                "avg_profit": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "recovery_factor": 0
            }
        
        # Calcular ganancias y pérdidas
        profits = [t["profit"] for t in self.trades]
        winning_trades = len([p for p in profits if p > 0])
        losing_trades = len([p for p in profits if p < 0])
        total_profit = sum(profits)
        
        # Win Rate
        win_rate = (winning_trades / len(self.trades)) * 100 if self.trades else 0
        
        # Profit Factor
        total_wins = sum([p for p in profits if p > 0])
        total_losses = sum([abs(p) for p in profits if p < 0])
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Drawdown máximo
        equity_array = np.array(self.equity_history)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = abs(np.min(drawdown)) * 100 if len(drawdown) > 0 else 0
        
        # Sharpe Ratio (retorno / volatilidad)
        if len(profits) > 1:
            returns = np.diff(self.equity_history) / self.equity_history[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Recovery Factor
        recovery_factor = total_profit / abs(np.min(drawdown) * self.initial_balance) if np.min(drawdown) < 0 else float('inf')
        
        # Compilar resultados
        results = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "total_trades": len(self.trades),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "profit_factor": round(profit_factor, 2),
            "avg_profit": round(total_profit / len(self.trades) if self.trades else 0, 2),
            "max_profit": round(max(profits) if profits else 0, 2),
            "max_loss": round(min(profits) if profits else 0, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "recovery_factor": round(recovery_factor, 2),
            "final_balance": round(self.current_balance, 2),
            "total_return": round(((self.current_balance - self.initial_balance) / self.initial_balance) * 100, 2)
        }
        
        logger.info(f"Backtest completado:")
        logger.info(f"  Total Trades: {results['total_trades']}")
        logger.info(f"  Win Rate: {results['win_rate']}%")
        logger.info(f"  Total Profit: ${results['total_profit']}")
        logger.info(f"  Profit Factor: {results['profit_factor']}")
        logger.info(f"  Max Drawdown: {results['max_drawdown']}%")
        
        return results

    def save_results(self, filename: str):
        """
        Guardar resultados del backtest en JSON
        
        Args:
            filename: Nombre del archivo para guardar
        """
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "trades": self.trades,
                    "equity_history": self.equity_history
                }, f, indent=2)
            logger.info(f"Resultados guardados en {filename}")
        except Exception as e:
            logger.error(f"Error al guardar resultados: {str(e)}")

    def get_trades_summary(self) -> str:
        """
        Obtener resumen de trades
        
        Returns:
            str: Resumen formateado
        """
        summary = "=== RESUMEN DE TRADES ===\n"
        summary += f"Total Trades: {len(self.trades)}\n"
        
        for i, trade in enumerate(self.trades, 1):
            summary += f"\nTrade {i}:\n"
            summary += f"  Tipo: {trade['type']}\n"
            summary += f"  Entrada: {trade['entry_price']:.5f}\n"
            summary += f"  Salida: {trade['close_price']:.5f}\n"
            summary += f"  Ganancia: ${trade['profit']:.2f}\n"
            summary += f"  Razón: {trade['reason']}\n"
        
        return summary
