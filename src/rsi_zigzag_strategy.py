"""Módulo integrado de estrategia RSI + ZigZag Arrow"""

import logging
import numpy as np
from typing import Optional, Tuple
from src.strategy import RSIStrategy
from src.zigzag_arrow import ZigZagArrow

logger = logging.getLogger(__name__)


class RSIZigZagStrategy:
    """Estrategia combinada RSI + ZigZag Arrow para más precisión"""

    def __init__(self, rsi_period: int = 14, rsi_oversold: int = 30, rsi_overbought: int = 70,
                 zigzag_threshold: float = 0.005, zigzag_min_bars: int = 5):
        """
        Inicializar estrategia combinada
        
        Args:
            rsi_period: Período RSI
            rsi_oversold: Nivel sobreventa RSI
            rsi_overbought: Nivel sobrecompra RSI
            zigzag_threshold: Umbral ZigZag
            zigzag_min_bars: Mínimo barras ZigZag
        """
        self.rsi = RSIStrategy(rsi_period, rsi_overbought, rsi_oversold)
        self.zigzag = ZigZagArrow(zigzag_threshold, zigzag_min_bars)
        logger.info("RSIZigZagStrategy inicializada")

    def analyze(self, prices: np.ndarray, highs: Optional[np.ndarray] = None,
               lows: Optional[np.ndarray] = None, 
               weight_rsi: float = 0.5, weight_zigzag: float = 0.5) -> Tuple[Optional[str], Dict]:
        """
        Analizar usando ambos indicadores
        
        Args:
            prices: Array de precios de cierre
            highs: Array de máximos
            lows: Array de mínimos
            weight_rsi: Peso del RSI en decisión (0-1)
            weight_zigzag: Peso del ZigZag en decisión (0-1)
            
        Returns:
            tuple: (signal, info_dict)
        """
        if highs is None:
            highs = prices
        if lows is None:
            lows = prices
        
        # Obtener señales de ambos indicadores
        rsi_value, rsi_signal = self.rsi.analyze(prices)
        zigzag_signal = self.zigzag.get_signal_from_zigzag(prices, highs, lows)
        trend = self.zigzag.get_current_trend()
        
        # Información detallada
        info = {
            "rsi_value": rsi_value,
            "rsi_signal": rsi_signal,
            "zigzag_signal": zigzag_signal,
            "zigzag_trend": trend,
            "combined_signal": None,
            "confidence": 0
        }
        
        try:
            # Lógica de combinación
            signal_score = 0
            confidence = 0
            
            # Si ambos coinciden, alta confianza
            if rsi_signal and zigzag_signal and rsi_signal == zigzag_signal:
                signal_score = 1 if rsi_signal == "BUY" else -1
                confidence = 0.95
                logger.info(f"✅ CONFIRMACIÓN FUERTE: RSI y ZigZag ambos {rsi_signal}")
            
            # Si solo RSI señala
            elif rsi_signal and not zigzag_signal:
                signal_score = (1 if rsi_signal == "BUY" else -1) * weight_rsi
                confidence = 0.60
                logger.info(f"⚠️ Solo RSI señala: {rsi_signal} (Confianza: 60%)")
            
            # Si solo ZigZag señala
            elif zigzag_signal and not rsi_signal:
                signal_score = (1 if zigzag_signal == "BUY" else -1) * weight_zigzag
                confidence = 0.70
                logger.info(f"⚠️ Solo ZigZag señala: {zigzag_signal} (Confianza: 70%)")
            
            # Convertir score a señal
            if signal_score > 0.5:
                info["combined_signal"] = "BUY"
                info["confidence"] = confidence
            elif signal_score < -0.5:
                info["combined_signal"] = "SELL"
                info["confidence"] = confidence
            else:
                info["combined_signal"] = None
                info["confidence"] = 0
            
            return info["combined_signal"], info
            
        except Exception as e:
            logger.error(f"Error en análisis combinado: {str(e)}")
            return None, info

    def get_pattern_info(self) -> Optional[Dict]:
        """Obtener información de patrones del ZigZag"""
        pattern = self.zigzag.identify_pattern()
        
        if pattern:
            return {
                "pattern": pattern,
                "type": "BUY" if "BUY" in pattern else "SELL",
                "pivots": self.zigzag.zigzag_points[-3:] if len(self.zigzag.zigzag_points) >= 3 else []
            }
        
        return None

    def print_combined_status(self, prices: np.ndarray):
        """Mostrar estado combinado"""
        logger.info("\n" + "=" * 60)
        logger.info("ANÁLISIS RSI + ZIGZAG ARROW")
        logger.info("=" * 60)
        
        # RSI status
        rsi_value, _ = self.rsi.analyze(prices)
        if rsi_value:
            logger.info(f"RSI: {rsi_value:.2f}")
            if rsi_value < self.rsi.oversold:
                logger.info(f"  Estado: 📉 SOBREVENTA (< {self.rsi.oversold})")
            elif rsi_value > self.rsi.overbought:
                logger.info(f"  Estado: 📈 SOBRECOMPRA (> {self.rsi.overbought})")
            else:
                logger.info(f"  Estado: ➡️ NEUTRAL")
        
        # ZigZag status
        if self.zigzag.zigzag_points:
            last_pivot = self.zigzag.zigzag_points[-1]
            logger.info(f"\nÚltimo ZigZag Pivot:")
            logger.info(f"  Tipo: {last_pivot['type']}")
            logger.info(f"  Precio: {last_pivot['price']:.5f}")
        
        # Pattern
        pattern_info = self.get_pattern_info()
        if pattern_info:
            logger.info(f"\nPatrón: {pattern_info['pattern']} {'🟢' if pattern_info['type'] == 'BUY' else '🔴'}")
        
        logger.info("=" * 60 + "\n")
