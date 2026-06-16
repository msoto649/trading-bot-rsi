"""Módulo de optimización de parámetros"""

import logging
import numpy as np
from typing import Dict, List, Tuple
from src.backtest_engine import BacktestEngine
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """Clase para optimizar parámetros de la estrategia"""

    def __init__(self, symbol: str, timeframe: int, initial_balance: float = 10000):
        """
        Inicializar optimizador de parámetros
        
        Args:
            symbol: Símbolo a optimizar
            timeframe: Timeframe en minutos
            initial_balance: Balance inicial para backtest
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.initial_balance = initial_balance
        self.optimization_results = []
        logger.info(f"ParameterOptimizer inicializado - Symbol: {symbol}")

    def optimize_rsi_parameters(self, prices: np.ndarray, strategy_func,
                               period_range: Tuple = (8, 20),
                               oversold_range: Tuple = (20, 40),
                               overbought_range: Tuple = (60, 80),
                               stop_loss_pips: float = 50,
                               take_profit_pips: float = 100) -> Dict:
        """
        Optimizar parámetros RSI (período, oversold, overbought)
        
        Args:
            prices: Array de precios históricos
            strategy_func: Función que retorna estrategia
            period_range: Rango de períodos RSI a probar
            oversold_range: Rango de niveles oversold
            overbought_range: Rango de niveles overbought
            stop_loss_pips: Stop loss para backtest
            take_profit_pips: Take profit para backtest
            
        Returns:
            dict: Mejores parámetros encontrados
        """
        logger.info("=" * 50)
        logger.info("INICIANDO OPTIMIZACIÓN DE PARÁMETROS RSI")
        logger.info("=" * 50)
        
        best_result = {
            "profit_factor": 0,
            "parameters": {},
            "metrics": {}
        }
        
        test_count = 0
        total_tests = (period_range[1] - period_range[0]) * \
                      (oversold_range[1] - oversold_range[0]) * \
                      (overbought_range[1] - overbought_range[0])
        
        logger.info(f"Total de combinaciones a probar: {total_tests}")
        
        try:
            for period in range(period_range[0], period_range[1] + 1):
                for oversold in range(oversold_range[0], oversold_range[1] + 1):
                    for overbought in range(overbought_range[0], overbought_range[1] + 1):
                        test_count += 1
                        
                        if overbought <= oversold:
                            continue
                        
                        params = {
                            "period": period,
                            "oversold": oversold,
                            "overbought": overbought
                        }
                        
                        backtest = BacktestEngine(self.symbol, self.timeframe, self.initial_balance)
                        results = backtest.backtest(
                            prices=prices,
                            strategy_func=strategy_func,
                            lot_size=0.1,
                            stop_loss_pips=stop_loss_pips,
                            take_profit_pips=take_profit_pips
                        )
                        
                        result_entry = {
                            "parameters": params,
                            "metrics": results,
                            "profit_factor": results.get("profit_factor", 0)
                        }
                        self.optimization_results.append(result_entry)
                        
                        if results.get("profit_factor", 0) > best_result["profit_factor"]:
                            best_result = result_entry
                        
                        if test_count % 10 == 0:
                            logger.info(f"Progreso: {test_count}/{total_tests} - "
                                       f"Mejor Profit Factor: {best_result['profit_factor']:.2f}")
            
            logger.info("\n" + "=" * 50)
            logger.info("RESULTADOS DE OPTIMIZACIÓN")
            logger.info("=" * 50)
            logger.info(f"Mejores parámetros encontrados:")
            logger.info(f"  Período RSI: {best_result['parameters']['period']}")
            logger.info(f"  Oversold: {best_result['parameters']['oversold']}")
            logger.info(f"  Overbought: {best_result['parameters']['overbought']}")
            logger.info(f"\nMétricas:")
            logger.info(f"  Profit Factor: {best_result['metrics']['profit_factor']:.2f}")
            logger.info(f"  Win Rate: {best_result['metrics']['win_rate']:.2f}%")
            logger.info(f"  Total Profit: ${best_result['metrics']['total_profit']:.2f}")
            logger.info(f"  Max Drawdown: {best_result['metrics']['max_drawdown']:.2f}%")
            logger.info("=" * 50)
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error durante optimización: {str(e)}")
            return best_result

    def get_top_results(self, limit: int = 10) -> List[Dict]:
        """
        Obtener los mejores resultados de optimización
        
        Args:
            limit: Cantidad de resultados a retornar
            
        Returns:
            list: Lista de mejores resultados ordenados
        """
        sorted_results = sorted(
            self.optimization_results,
            key=lambda x: x['metrics'].get('profit_factor', 0),
            reverse=True
        )
        
        logger.info("\n" + "=" * 50)
        logger.info("TOP 10 MEJORES COMBINACIONES")
        logger.info("=" * 50)
        
        for i, result in enumerate(sorted_results[:limit], 1):
            logger.info(f"\n{i}. Profit Factor: {result['metrics']['profit_factor']:.2f}")
            logger.info(f"   Parámetros: {result['parameters']}")
            logger.info(f"   Win Rate: {result['metrics']['win_rate']:.2f}%")
            logger.info(f"   Total Profit: ${result['metrics']['total_profit']:.2f}")
        
        logger.info("=" * 50 + "\n")
        
        return sorted_results[:limit]