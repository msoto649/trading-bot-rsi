"""Módulo de filtros de señal - Signal Filter"""

import logging
import numpy as np
from datetime import datetime
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SignalFilter:
    """Clase para filtrar y mejorar señales de trading"""

    def __init__(self, ma_fast: int = 50, ma_slow: int = 200, atr_period: int = 14):
        """
        Inicializar filtros de señal
        
        Args:
            ma_fast: Período de media móvil rápida (default: 50)
            ma_slow: Período de media móvil lenta (default: 200)
            atr_period: Período de ATR para volatilidad (default: 14)
        """
        self.ma_fast = ma_fast
        self.ma_slow = ma_slow
        self.atr_period = atr_period
        logger.info(f"SignalFilter inicializado - MA Fast: {ma_fast}, MA Slow: {ma_slow}, ATR: {atr_period}")

    def get_trend(self, prices: np.ndarray) -> Optional[str]:
        """
        Determinar tendencia usando medias móviles
        
        Args:
            prices: Array de precios de cierre
            
        Returns:
            str: 'UPTREND', 'DOWNTREND' o None si datos insuficientes
        """
        if len(prices) < self.ma_slow:
            logger.warning(f"Datos insuficientes para tendencia. Se necesitan {self.ma_slow}, tengo {len(prices)}")
            return None
        
        try:
            ma_fast = np.mean(prices[-self.ma_fast:])
            ma_slow = np.mean(prices[-self.ma_slow:])
            
            if ma_fast > ma_slow:
                trend = "UPTREND"
            elif ma_fast < ma_slow:
                trend = "DOWNTREND"
            else:
                trend = "NEUTRAL"
            
            logger.debug(f"Tendencia: {trend} (MA50: {ma_fast:.5f}, MA200: {ma_slow:.5f})")
            return trend
            
        except Exception as e:
            logger.error(f"Error al calcular tendencia: {str(e)}")
            return None

    def filter_signal_by_trend(self, signal: str, trend: str) -> Optional[str]:
        """
        Filtrar señal según tendencia - no operar contra la tendencia
        
        Args:
            signal: Señal original ('BUY', 'SELL' o None)
            trend: Tendencia ('UPTREND', 'DOWNTREND', 'NEUTRAL')
            
        Returns:
            str: Señal filtrada o None si contradice la tendencia
        """
        if not signal or not trend:
            return signal
        
        # No operar SELL en uptrend
        if signal == "SELL" and trend == "UPTREND":
            logger.debug("Señal SELL filtrada - Contradice UPTREND")
            return None
        
        # No operar BUY en downtrend
        if signal == "BUY" and trend == "DOWNTREND":
            logger.debug("Señal BUY filtrada - Contradice DOWNTREND")
            return None
        
        return signal

    def calculate_atr(self, prices: np.ndarray) -> float:
        """
        Calcular Average True Range (volatilidad)
        
        Args:
            prices: Array de precios (usando close)
            
        Returns:
            float: Valor de ATR
        """
        if len(prices) < self.atr_period:
            logger.warning(f"Datos insuficientes para ATR. Se necesitan {self.atr_period}, tengo {len(prices)}")
            return 0
        
        try:
            recent_prices = prices[-self.atr_period:]
            atr = np.std(recent_prices)
            logger.debug(f"ATR calculado: {atr:.5f}")
            return atr
            
        except Exception as e:
            logger.error(f"Error al calcular ATR: {str(e)}")
            return 0

    def is_trading_hours(self, hour: int = None) -> bool:
        """
        Verificar si es hora de operar (evita volatilidad extrema)
        
        Args:
            hour: Hora en UTC (si None, usa la hora actual)
            
        Returns:
            bool: True si es hora de operar
        """
        if hour is None:
            hour = datetime.utcnow().hour
        
        # Horas de trading: 6:00 - 20:00 UTC (mejor liquidez)
        # Evita: 0:00 - 6:00 (madrugada) y 20:00 - 24:00 (cierre de mercado)
        
        if hour < 6 or hour >= 20:
            logger.debug(f"Fuera de horas de trading (Hora UTC: {hour}:00)")
            return False
        
        return True

    def filter_by_volatility(self, signal: str, atr: float, volatility_threshold: float = 0.001) -> Optional[str]:
        """
        Filtrar señales por volatilidad extrema
        
        Args:
            signal: Señal original
            atr: Volatilidad actual (ATR)
            volatility_threshold: Umbral de volatilidad máxima
            
        Returns:
            str: Señal filtrada o None si volatilidad es extrema
        """
        if not signal or atr == 0:
            return signal
        
        if atr > volatility_threshold:
            logger.warning(f"Volatilidad extrema detectada (ATR: {atr:.5f} > {volatility_threshold})")
            return None
        
        return signal

    def apply_all_filters(self, signal: str, prices: np.ndarray, 
                         apply_trend_filter: bool = True,
                         apply_hours_filter: bool = True,
                         apply_volatility_filter: bool = True) -> Optional[str]:
        """
        Aplicar todos los filtros disponibles
        
        Args:
            signal: Señal original
            prices: Array de precios
            apply_trend_filter: Si True, aplica filtro de tendencia
            apply_hours_filter: Si True, aplica filtro de horas
            apply_volatility_filter: Si True, aplica filtro de volatilidad
            
        Returns:
            str: Señal filtrada o None
        """
        if not signal:
            return None
        
        filtered_signal = signal
        
        # Filtro de horas
        if apply_hours_filter and not self.is_trading_hours():
            logger.debug("Señal rechazada - Fuera de horas de trading")
            return None
        
        # Filtro de tendencia
        if apply_trend_filter:
            trend = self.get_trend(prices)
            filtered_signal = self.filter_signal_by_trend(filtered_signal, trend)
            if not filtered_signal:
                logger.debug("Señal rechazada - Contradice la tendencia")
                return None
        
        # Filtro de volatilidad
        if apply_volatility_filter:
            atr = self.calculate_atr(prices)
            filtered_signal = self.filter_by_volatility(filtered_signal, atr)
            if not filtered_signal:
                logger.debug("Señal rechazada - Volatilidad extrema")
                return None
        
        logger.info(f"Señal validada: {filtered_signal}")
        return filtered_signal

    def print_filter_status(self, prices: np.ndarray):
        """Mostrar estado de todos los filtros"""
        try:
            trend = self.get_trend(prices)
            atr = self.calculate_atr(prices)
            trading_hours = self.is_trading_hours()
            current_hour = datetime.utcnow().hour
            
            logger.info("\n" + "=" * 50)
            logger.info("ESTADO DE FILTROS")
            logger.info("=" * 50)
            logger.info(f"Tendencia: {trend}")
            logger.info(f"ATR (Volatilidad): {atr:.5f}")
            logger.info(f"Hora UTC: {current_hour}:00")
            logger.info(f"Horas de Trading: {'✅' if trading_hours else '❌'}")
            logger.info("=" * 50 + "\n")
            
        except Exception as e:
            logger.error(f"Error al mostrar estado de filtros: {str(e)}")