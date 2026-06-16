"""Módulo de gestión de riesgo - Risk Manager"""

import logging
from typing import Dict, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class RiskManager:
    """Clase para gestionar el riesgo y dinero en operaciones de trading"""

    def __init__(self, account_balance: float, risk_per_trade: float = 2.0, 
                 max_daily_loss: float = 5.0, max_position_size: float = 0.5):
        """
        Inicializar gestor de riesgo
        
        Args:
            account_balance: Balance actual de la cuenta
            risk_per_trade: Porcentaje de balance a arriesgar por trade (default: 2%)
            max_daily_loss: Máximo porcentaje de pérdida diaria (default: 5%)
            max_position_size: Tamaño máximo de posición en lotes (default: 0.5)
        """
        self.account_balance = account_balance
        self.initial_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size
        self.daily_loss = 0.0
        self.trades_today = []
        
        logger.info(f"RiskManager inicializado - Balance: ${account_balance:.2f}, "
                   f"Riesgo por trade: {risk_per_trade}%, "
                   f"Pérdida diaria máx: {max_daily_loss}%")

    def calculate_lot_size(self, stop_loss_pips: float, pip_value: float = 0.0001) -> float:
        """
        Calcular tamaño de lote basado en riesgo
        
        Args:
            stop_loss_pips: Stop loss en pips
            pip_value: Valor de 1 pip (default: 0.0001 para forex)
            
        Returns:
            float: Tamaño de lote recomendado
        """
        try:
            # Calcular dinero a arriesgar
            risk_money = self.account_balance * (self.risk_per_trade / 100)
            
            # Calcular lot_size basado en SL
            lot_size = risk_money / (stop_loss_pips * pip_value)
            
            # Limitar al máximo permitido
            lot_size = min(lot_size, self.max_position_size)
            
            logger.debug(f"Lot size calculado: {lot_size:.2f} (Riesgo: ${risk_money:.2f})")
            return lot_size
            
        except Exception as e:
            logger.error(f"Error al calcular lot size: {str(e)}")
            return 0.01  # Retornar mínimo si hay error

    def calculate_dynamic_sl_tp(self, entry_price: float, atr: float, 
                               position_type: str = "BUY") -> Tuple[float, float]:
        """
        Calcular Stop Loss y Take Profit dinámicos basados en ATR
        
        Args:
            entry_price: Precio de entrada
            atr: Average True Range (volatilidad actual)
            position_type: Tipo de posición (BUY/SELL)
            
        Returns:
            tuple: (stop_loss_price, take_profit_price)
        """
        try:
            # Multiplicadores de ATR
            sl_multiplier = 1.5  # SL = 1.5x ATR
            tp_multiplier = 3.0  # TP = 3x ATR
            
            if position_type == "BUY":
                stop_loss = entry_price - (atr * sl_multiplier)
                take_profit = entry_price + (atr * tp_multiplier)
            else:  # SELL
                stop_loss = entry_price + (atr * sl_multiplier)
                take_profit = entry_price - (atr * tp_multiplier)
            
            logger.debug(f"SL/TP dinámicos calculados - SL: {stop_loss:.5f}, TP: {take_profit:.5f}")
            return stop_loss, take_profit
            
        except Exception as e:
            logger.error(f"Error al calcular SL/TP dinámicos: {str(e)}")
            return None, None

    def calculate_atr(self, prices: np.ndarray, period: int = 14) -> float:
        """
        Calcular Average True Range (ATR) - medida de volatilidad
        
        Args:
            prices: Array de precios (o closes)
            period: Período de ATR (default: 14)
            
        Returns:
            float: Valor de ATR
        """
        try:
            if len(prices) < period + 1:
                logger.warning(f"Datos insuficientes para ATR. Se necesitan {period + 1}, tengo {len(prices)}")
                return 0
            
            # Para simplificar, usamos la diferencia estándar
            # En producción, usarías true range (high-low, high-close, low-close)
            recent_prices = prices[-period:]
            atr = np.std(recent_prices)
            
            logger.debug(f"ATR calculado: {atr:.5f}")
            return atr
            
        except Exception as e:
            logger.error(f"Error al calcular ATR: {str(e)}")
            return 0

    def is_daily_loss_exceeded(self, current_loss: float) -> bool:
        """
        Verificar si se ha excedido la pérdida diaria máxima
        
        Args:
            current_loss: Pérdida actual del día en dinero
            
        Returns:
            bool: True si la pérdida excede el máximo permitido
        """
        max_loss_money = self.initial_balance * (self.max_daily_loss / 100)
        
        if current_loss > max_loss_money:
            logger.warning(f"⚠️ Pérdida diaria máxima excedida: ${current_loss:.2f} > ${max_loss_money:.2f}")
            return True
        
        return False

    def check_risk_parameters(self, stop_loss_pips: float, take_profit_pips: float) -> bool:
        """
        Verificar que los parámetros de riesgo sean válidos
        
        Args:
            stop_loss_pips: Stop loss en pips
            take_profit_pips: Take profit en pips
            
        Returns:
            bool: True si los parámetros son válidos
        """
        # Verificar que TP sea mayor que SL
        if take_profit_pips <= stop_loss_pips:
            logger.error(f"Take Profit ({take_profit_pips}) debe ser mayor que Stop Loss ({stop_loss_pips})")
            return False
        
        # Verificar ratio riesgo/recompensa
        risk_reward_ratio = take_profit_pips / stop_loss_pips
        if risk_reward_ratio < 1.5:
            logger.warning(f"⚠️ Ratio riesgo/recompensa bajo: {risk_reward_ratio:.2f} (recomendado: >1.5)")
        
        logger.debug(f"Parámetros de riesgo validados - Ratio R/R: {risk_reward_ratio:.2f}")
        return True

    def update_balance(self, new_balance: float):
        """
        Actualizar balance de la cuenta
        
        Args:
            new_balance: Nuevo balance
        """
        self.account_balance = new_balance
        logger.debug(f"Balance actualizado: ${new_balance:.2f}")

    def record_trade(self, trade_result: Dict):
        """
        Registrar resultado de trade para tracking diario
        
        Args:
            trade_result: Diccionario con resultado del trade
        """
        self.trades_today.append(trade_result)
        
        if trade_result["profit"] < 0:
            self.daily_loss += abs(trade_result["profit"])
        
        logger.info(f"Trade registrado - Ganancia: ${trade_result['profit']:.2f}, "
                   f"Pérdida diaria acumulada: ${self.daily_loss:.2f}")

    def get_daily_summary(self) -> Dict:
        """
        Obtener resumen del día
        
        Returns:
            dict: Resumen de operaciones del día
        """
        total_profit = sum([t.get("profit", 0) for t in self.trades_today])
        winning_trades = len([t for t in self.trades_today if t.get("profit", 0) > 0])
        losing_trades = len([t for t in self.trades_today if t.get("profit", 0) < 0])
        
        summary = {
            "total_trades": len(self.trades_today),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "total_profit": round(total_profit, 2),
            "daily_loss": round(self.daily_loss, 2),
            "win_rate": round((winning_trades / len(self.trades_today) * 100) if self.trades_today else 0, 2),
            "current_balance": round(self.account_balance, 2),
            "balance_change": round(self.account_balance - self.initial_balance, 2)
        }
        
        return summary

    def should_stop_trading(self) -> bool:
        """
        Determinar si se debe detener el trading por límites de riesgo
        
        Returns:
            bool: True si se debe detener
        """
        # Verificar pérdida diaria
        if self.is_daily_loss_exceeded(self.daily_loss):
            logger.warning("🛑 Trading detenido - Pérdida diaria máxima excedida")
            return True
        
        # Verificar si el balance está muy bajo
        balance_drawdown = ((self.initial_balance - self.account_balance) / self.initial_balance) * 100
        if balance_drawdown > 20:  # Más del 20% de drawdown
            logger.warning(f"🛑 Trading detenido - Drawdown crítico: {balance_drawdown:.2f}%")
            return True
        
        return False

    def calculate_position_size_scaling(self, current_profit: float) -> float:
        """
        Calcular factor de escala de posición basado en ganancias/pérdidas
        
        Args:
            current_profit: Ganancia actual acumulada
            
        Returns:
            float: Factor multiplicador para lot_size (1.0 = sin cambios)
        """
        # Si estamos en ganancias, aumentar agresividad
        if current_profit > 0:
            profit_percentage = (current_profit / self.initial_balance) * 100
            
            if profit_percentage > 10:
                scale = 1.5  # 50% más agresivo
            elif profit_percentage > 5:
                scale = 1.25  # 25% más agresivo
            else:
                scale = 1.0
        else:
            # Si estamos en pérdidas, reducir agresividad
            loss_percentage = abs((current_profit / self.initial_balance) * 100)
            
            if loss_percentage > 10:
                scale = 0.5  # 50% menos agresivo
            elif loss_percentage > 5:
                scale = 0.75  # 25% menos agresivo
            else:
                scale = 1.0
        
        logger.debug(f"Factor de escala calculado: {scale} (Ganancia: ${current_profit:.2f})")
        return scale

    def print_risk_status(self):
        """Mostrar estado actual del riesgo"""
        summary = self.get_daily_summary()
        
        logger.info("\n" + "=" * 50)
        logger.info("ESTADO DE RIESGO")
        logger.info("=" * 50)
        logger.info(f"Balance Inicial: ${self.initial_balance:.2f}")
        logger.info(f"Balance Actual: ${summary['current_balance']:.2f}")
        logger.info(f"Cambio de Balance: ${summary['balance_change']:.2f}")
        logger.info(f"Trades Hoy: {summary['total_trades']}")
        logger.info(f"Win Rate: {summary['win_rate']}%")
        logger.info(f"Ganancia Total: ${summary['total_profit']:.2f}")
        logger.info(f"Pérdida Diaria: ${summary['daily_loss']:.2f}")
        logger.info(f"Límite Diario: ${self.initial_balance * (self.max_daily_loss / 100):.2f}")
        logger.info("=" * 50 + "\n")
