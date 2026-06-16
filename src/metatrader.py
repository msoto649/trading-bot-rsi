"""Módulo de conexión a MetaTrader 5"""

import MetaTrader5 as mt5
import logging
from typing import Optional, List
import pytz
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class MetaTrader5Connection:
    """Clase para gestionar la conexión a MetaTrader 5"""

    def __init__(self, account: int, password: str, server: str):
        """
        Inicializar la conexión a MT5
        
        Args:
            account: Número de cuenta
            password: Contraseña de la cuenta
            server: Servidor (ej: XMGlobal-MT5)
        """
        self.account = account
        self.password = password
        self.server = server
        self.connected = False

    def connect(self) -> bool:
        """
        Conectar a MetaTrader 5
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Inicializa MT5
            if not mt5.initialize():
                logger.error("No se pudo inicializar MT5")
                return False

            # Pequeña pausa para que MT5 se establezca
            time.sleep(0.5)

            # Intenta login con el servidor especificado
            login_result = mt5.login(self.account, self.password, self.server)
            
            if not login_result:
                error = mt5.last_error()
                logger.error(f"No se pudo conectar con cuenta {self.account} en servidor {self.server}")
                logger.error(f"Error detallado: {error}")
                return False

            self.connected = True
            logger.info(f"Conectado a MT5 - Cuenta: {self.account}")
            return True

        except Exception as e:
            logger.error(f"Error al conectar a MT5: {str(e)}")
            return False

    def disconnect(self):
        """Desconectar de MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("Desconectado de MT5")

    def get_account_info(self) -> dict:
        """
        Obtener información de la cuenta
        
        Returns:
            dict: Información de la cuenta
        """
        try:
            info = mt5.account_info()
            if info:
                return {
                    "balance": info.balance,
                    "equity": info.equity,
                    "margin": info.margin,
                    "margin_level": info.margin_level,
                    "profit": info.profit,
                    "free_margin": info.margin_free
                }
            return {}
        except Exception as e:
            logger.error(f"Error al obtener información de cuenta: {str(e)}")
            return {}

    def get_symbol_info(self, symbol: str) -> dict:
        """
        Obtener información del símbolo
        
        Args:
            symbol: Símbolo a consultar (ej: AUDUSD_CL)
            
        Returns:
            dict: Información del símbolo
        """
        try:
            info = mt5.symbol_info(symbol)
            if info:
                return {
                    "symbol": info.name,
                    "bid": info.bid,
                    "ask": info.ask,
                    "spread": info.spread,
                    "tick_size": info.trade_tick_size,
                    "contract_size": info.trade_contract_size
                }
            logger.warning(f"Símbolo {symbol} no encontrado")
            return {}
        except Exception as e:
            logger.error(f"Error al obtener información de símbolo: {str(e)}")
            return {}

    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> Optional[list]:
        """
        Obtener barras de precios
        
        Args:
            symbol: Símbolo (ej: AUDUSD_CL)
            timeframe: Timeframe en minutos (1, 5, 15, 30, 60, etc.)
            count: Cantidad de barras a obtener
            
        Returns:
            list: Lista de barras o None si hay error
        """
        try:
            # Convertir minutos a constante de MT5
            tf_map = {
                1: mt5.TIMEFRAME_M1,
                5: mt5.TIMEFRAME_M5,
                15: mt5.TIMEFRAME_M15,
                30: mt5.TIMEFRAME_M30,
                60: mt5.TIMEFRAME_H1,
                240: mt5.TIMEFRAME_H4,
                1440: mt5.TIMEFRAME_D1
            }
            
            tf = tf_map.get(timeframe, mt5.TIMEFRAME_M15)
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            
            if rates is None:
                logger.error(f"Error al obtener rates de {symbol}")
                return None
                
            return list(rates)
            
        except Exception as e:
            logger.error(f"Error al obtener rates: {str(e)}")
            return None

    def get_positions(self) -> List[dict]:
        """
        Obtener posiciones abiertas
        
        Returns:
            list: Lista de posiciones abiertas
        """
        try:
            positions = mt5.positions_get()
            if positions:
                return [
                    {
                        "ticket": pos.ticket,
                        "symbol": pos.symbol,
                        "type": "BUY" if pos.type == 0 else "SELL",
                        "volume": pos.volume,
                        "open_price": pos.price_open,
                        "current_price": pos.price_current,
                        "profit": pos.profit,
                        "sl": pos.sl,
                        "tp": pos.tp
                    }
                    for pos in positions
                ]
            return []
        except Exception as e:
            logger.error(f"Error al obtener posiciones: {str(e)}")
            return []

    def is_connected(self) -> bool:
        """Verificar si está conectado a MT5"""
        return self.connected and mt5.terminal_info() is not None
