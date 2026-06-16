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
            server: Servidor (ej: LiteFinance-MT5)
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
            logger.debug(f"Conectando a MT5 con cuenta: {self.account}, servidor: {self.server}")
            
            # Inicializa MT5
            logger.debug("Llamando a mt5.initialize()...")
            init_result = mt5.initialize()
            logger.debug(f"mt5.initialize() retorno: {init_result}")
            
            if not init_result:
                logger.error("No se pudo inicializar MT5")
                return False

            # Pequeña pausa para que MT5 se establezca
            time.sleep(0.5)

            logger.debug(f"Intentando login con servidor: {self.server}")
            # Intenta login - parámetros nombrados según API de MetaTrader5
            login_result = mt5.login(login=self.account, password=self.password, server=self.server)
            
            logger.debug(f"mt5.login() retorno: {login_result}")
            
            if not login_result:
                error = mt5.last_error()
                logger.error(f"No se pudo conectar con cuenta {self.account} en servidor {self.server}")
                logger.error(f"Error detallado: {error}")
                return False

            # Verificar que realmente estamos conectados
            terminal_info = mt5.terminal_info()
            logger.debug(f"Terminal info: {terminal_info}")
            
            if not terminal_info or not terminal_info.connected:
                logger.error("Terminal no esta conectado despues del login")
                return False

            self.connected = True
            logger.info(f"Conectado a MT5 - Cuenta: {self.account}")
            return True

        except Exception as e:
            logger.error(f"Error al conectar a MT5: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def disconnect(self):
        """Desconectar de MetaTrader 5"""
        if self.connected:
            try:
                mt5.shutdown()
            except:
                pass
            self.connected = False
            logger.info("Desconectado de MT5")

    def get_account_info(self) -> dict:
        """
        Obtener informacion de la cuenta
        
        Returns:
            dict: Informacion de la cuenta
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
            logger.error(f"Error al obtener informacion de cuenta: {str(e)}")
            return {}

    def get_symbol_info(self, symbol: str) -> dict:
        """
        Obtener informacion del simbolo
        
        Args:
            symbol: Simbolo a consultar (ej: AUDUSD_CL)
            
        Returns:
            dict: Informacion del simbolo
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
            logger.warning(f"Simbolo {symbol} no encontrado")
            return {}
        except Exception as e:
            logger.error(f"Error al obtener informacion de simbolo: {str(e)}")
            return {}

    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> Optional[list]:
        """
        Obtener barras de precios
        
        Args:
            symbol: Simbolo (ej: AUDUSD_CL)
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
        """Verificar si esta conectado a MT5"""
        return self.connected and mt5.terminal_info() is not None
