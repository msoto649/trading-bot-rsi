"""Módulo de estrategia RSI"""

import logging
import numpy as np
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class RSIStrategy:
    """Clase para implementar la estrategia RSI"""

    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        """
        Inicializar estrategia RSI
        
        Args:
            period: Período del RSI (default: 14)
            overbought: Nivel de sobrecompra (default: 70)
            oversold: Nivel de sobreventa (default: 30)
        """
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.rsi_values = []
        logger.info(f"Estrategia RSI inicializada - Período: {period}, OB: {overbought}, OS: {oversold}")

    def calculate_rsi(self, prices: np.ndarray) -> Optional[float]:
        """
        Calcular RSI
        
        Args:
            prices: Array de precios de cierre
            
        Returns:
            float: Valor del RSI o None si no hay suficientes datos
        """
        if len(prices) < self.period + 1:
            logger.warning(f"Datos insuficientes para calcular RSI. Se necesitan {self.period + 1}, tengo {len(prices)}")
            return None

        try:
            # Calcular cambios
            deltas = np.diff(prices)
            
            # Separar ganancias y pérdidas
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calcular promedios móviles
            avg_gain = np.mean(gains[-self.period:])
            avg_loss = np.mean(losses[-self.period:])
            
            # Evitar división por cero
            if avg_loss == 0:
                rsi = 100 if avg_gain > 0 else 50
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            self.rsi_values.append(rsi)
            return rsi
            
        except Exception as e:
            logger.error(f"Error al calcular RSI: {str(e)}")
            return None

    def get_signal(self, rsi: float) -> Optional[str]:
        """
        Obtener señal de trading basada en RSI
        
        Args:
            rsi: Valor del RSI
            
        Returns:
            str: 'BUY', 'SELL' o None sin señal
        """
        if rsi is None:
            return None
            
        if rsi < self.oversold:
            logger.info(f"Señal BUY detectada - RSI: {rsi:.2f} < {self.oversold}")
            return "BUY"
        elif rsi > self.overbought:
            logger.info(f"Señal SELL detectada - RSI: {rsi:.2f} > {self.overbought}")
            return "SELL"
        
        return None

    def analyze(self, prices: np.ndarray) -> Tuple[Optional[float], Optional[str]]:
        """
        Analizar precios y generar señal
        
        Args:
            prices: Array de precios de cierre
            
        Returns:
            tuple: (valor RSI, señal de trading)
        """
        rsi = self.calculate_rsi(prices)
        if rsi is not None:
            signal = self.get_signal(rsi)
            return rsi, signal
        return None, None

    def get_rsi_history(self, limit: int = 10) -> list:
        """
        Obtener histórico de valores RSI
        
        Args:
            limit: Cantidad de valores a retornar
            
        Returns:
            list: Últimos valores de RSI
        """
        return self.rsi_values[-limit:]
