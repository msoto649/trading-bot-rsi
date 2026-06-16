"""Archivo principal - Trading Bot RSI con Backtesting y Risk Management"""

import json
import logging
import signal
import sys
import time
import numpy as np
from datetime import datetime
from pathlib import Path

from src.logger import setup_logger
from src.metatrader import MetaTrader5Connection
from src.strategy import RSIStrategy
from src.orders import OrderManager
from src.backtest_engine import BacktestEngine
from src.risk_manager import RiskManager

# Inicializar logger
logger = setup_logger()


class TradingBot:
    """Bot de trading automático con estrategia RSI, backtesting y gestión de riesgo"""

    def __init__(self, config_file: str = "config.json"):
        """
        Inicializar el bot de trading
        
        Args:
            config_file: Ruta del archivo de configuración
        """
        self.config = self._load_config(config_file)
        self.running = False
        self.trades_today = 0
        
        # Inicializar componentes
        self.mt5 = MetaTrader5Connection(
            self.config["account_number"],
            self.config["password"],
            self.config["server"]
        )
        
        self.strategy = RSIStrategy(
            period=self.config["rsi_period"],
            overbought=self.config["rsi_overbought"],
            oversold=self.config["rsi_oversold"]
        )
        
        self.order_manager = OrderManager(
            symbol=self.config["symbol"],
            lot_size=self.config["lot_size"],
            stop_loss_pips=self.config["stop_loss_pips"],
            take_profit_pips=self.config["take_profit_pips"]
        )
        
        # Backtesting engine
        self.backtest_engine = BacktestEngine(
            symbol=self.config["symbol"],
            timeframe=self.config["timeframe"],
            initial_balance=10000  # Balance de prueba para backtest
        )
        
        # Risk Manager - será inicializado después de conectar con MT5
        self.risk_manager = None
        
        logger.info("Bot inicializado correctamente")

    def _load_config(self, config_file: str) -> dict:
        """
        Cargar configuración desde archivo JSON
        
        Args:
            config_file: Ruta del archivo de configuración
            
        Returns:
            dict: Configuración del bot
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuración cargada desde {config_file}")
            return config
        except Exception as e:
            logger.error(f"Error al cargar configuración: {str(e)}")
            sys.exit(1)

    def initialize(self) -> bool:
        """
        Inicializar conexión a MetaTrader 5 y Risk Manager
        
        Returns:
            bool: True si la inicialización es exitosa
        """
        logger.info("=" * 50)
        logger.info("INICIALIZANDO BOT DE TRADING RSI")
        logger.info("=" * 50)
        
        if not self.mt5.connect():
            logger.error("No se pudo conectar a MetaTrader 5")
            return False
        
        # Obtener información de cuenta
        account_info = self.mt5.get_account_info()
        
        if not account_info:
            logger.error("No se pudo obtener información de la cuenta")
            return False
        
        initial_balance = account_info.get('balance', 0)
        
        if initial_balance <= 0:
            logger.error("Balance inválido o cuenta vacía")
            return False
        
        logger.info(f"Balance: ${initial_balance:.2f}")
        logger.info(f"Equity: ${account_info.get('equity', 'N/A'):.2f}")
        logger.info(f"Margen libre: ${account_info.get('free_margin', 'N/A'):.2f}")
        
        # Inicializar Risk Manager
        self.risk_manager = RiskManager(
            account_balance=initial_balance,
            risk_per_trade=self.config.get("risk_per_trade", 2.0),
            max_daily_loss=self.config.get("max_daily_loss", 5.0),
            max_position_size=self.config.get("max_position_size", 0.5)
        )
        
        # Obtener información del símbolo
        symbol_info = self.mt5.get_symbol_info(self.config["symbol"])
        
        if not symbol_info:
            logger.error(f"No se pudo obtener información del símbolo {self.config['symbol']}")
            return False
        
        logger.info(f"Símbolo: {symbol_info.get('symbol', 'N/A')}")
        logger.info(f"Bid: {symbol_info.get('bid', 'N/A'):.5f}")
        logger.info(f"Ask: {symbol_info.get('ask', 'N/A'):.5f}")
        logger.info(f"Spread: {symbol_info.get('spread', 'N/A')} pips")
        
        # Validar parámetros de riesgo
        if not self.risk_manager.check_risk_parameters(
            self.config["stop_loss_pips"],
            self.config["take_profit_pips"]
        ):
            logger.warning("⚠️ Parámetros de riesgo inválidos o subóptimos")
        
        logger.info(f"Trading habilitado: {self.config['trading_enabled']}")
        
        if not self.config["trading_enabled"]:
            logger.warning("⚠️ MODO DEMO - Trading deshabilitado en config.json")
        
        return True

    def run_backtest(self, bars: int = 500) -> dict:
        """
        Ejecutar backtesting de la estrategia
        
        Args:
            bars: Cantidad de barras históricas para backtestear
            
        Returns:
            dict: Resultados del backtest
        """
        logger.info("=" * 50)
        logger.info("EJECUTANDO BACKTESTING")
        logger.info("=" * 50)
        
        # Obtener datos históricos
        rates = self.mt5.get_rates(
            self.config["symbol"],
            self.config["timeframe"],
            bars
        )
        
        if not rates or len(rates) == 0:
            logger.error("No se pudieron obtener datos históricos")
            return {}
        
        # Extraer precios de cierre
        prices = np.array([rate[4] for rate in rates])  # close price
        logger.info(f"Datos históricos: {len(prices)} barras cargadas")
        
        # Función wrapper para la estrategia
        def strategy_func(price_array):
            rsi, signal = self.strategy.analyze(price_array)
            return signal
        
        # Calcular lot_size dinámico usando Risk Manager
        dynamic_lot_size = self.risk_manager.calculate_lot_size(
            self.config["stop_loss_pips"]
        )
        
        logger.info(f"Lot size dinámico calculado: {dynamic_lot_size:.2f}")
        
        # Ejecutar backtest
        results = self.backtest_engine.backtest(
            prices=prices,
            strategy_func=strategy_func,
            lot_size=dynamic_lot_size,
            stop_loss_pips=self.config["stop_loss_pips"],
            take_profit_pips=self.config["take_profit_pips"]
        )
        
        # Mostrar resultados
        logger.info("\n" + "=" * 50)
        logger.info("RESULTADOS DEL BACKTEST")
        logger.info("=" * 50)
        logger.info(f"Total Trades: {results['total_trades']}")
        logger.info(f"Win Rate: {results['win_rate']}%")
        logger.info(f"Total Profit: ${results['total_profit']:.2f}")
        logger.info(f"Profit Factor: {results['profit_factor']:.2f}")
        logger.info(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"Final Balance: ${results['final_balance']:.2f}")
        logger.info(f"Total Return: {results['total_return']:.2f}%")
        logger.info("=" * 50 + "\n")
        
        # Guardar resultados
        backtest_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.backtest_engine.save_results(backtest_file)
        
        return results

    def check_signal(self) -> str:
        """
        Verificar señal de trading
        
        Returns:
            str: 'BUY', 'SELL' o None
        """
        try:
            # Obtener rates
            rates = self.mt5.get_rates(
                self.config["symbol"],
                self.config["timeframe"],
                50
            )
            
            if not rates or len(rates) < 2:
                logger.warning("Datos insuficientes para análisis")
                return None
            
            # Extraer precios
            prices = np.array([rate[4] for rate in rates])
            
            # Analizar
            rsi, signal = self.strategy.analyze(prices)
            
            if rsi is not None:
                logger.debug(f"RSI: {rsi:.2f}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error al verificar señal: {str(e)}")
            return None

    def execute_trade(self, signal: str) -> bool:
        """
        Ejecutar trade basado en señal con gestión de riesgo
        
        Args:
            signal: 'BUY' o 'SELL'
            
        Returns:
            bool: True si se ejecutó la orden
        """
        if not signal or not self.config["trading_enabled"]:
            return False
        
        try:
            # Verificar si debe detener trading por límites de riesgo
            if self.risk_manager.should_stop_trading():
                logger.error("🛑 Trading detenido por límites de riesgo")
                self.running = False
                return False
            
            # Obtener precio actual
            rates = self.mt5.get_rates(self.config["symbol"], self.config["timeframe"], 1)
            if not rates:
                logger.error("No se pudo obtener precio actual")
                return False
            
            current_price = rates[0][4]
            
            # Verificar posiciones abiertas
            positions = self.order_manager.get_open_positions()
            if len(positions) >= self.config["max_positions"]:
                logger.warning(f"Máximo de posiciones alcanzado ({self.config['max_positions']})")
                return False
            
            # Calcular lot_size dinámico con Risk Manager
            account_info = self.mt5.get_account_info()
            self.risk_manager.update_balance(account_info.get('balance', 0))
            
            # Calcular escala de posición basada en ganancias/pérdidas
            current_profit = account_info.get('profit', 0)
            scale_factor = self.risk_manager.calculate_position_size_scaling(current_profit)
            
            dynamic_lot_size = self.risk_manager.calculate_lot_size(
                self.config["stop_loss_pips"]
            ) * scale_factor
            
            logger.info(f"Lot size ajustado: {dynamic_lot_size:.2f} (Escala: {scale_factor:.2f}x)")
            
            # Actualizar lot_size en order manager
            self.order_manager.lot_size = dynamic_lot_size
            
            # Enviar orden
            ticket = self.order_manager.send_order(signal, current_price)
            
            if ticket:
                self.trades_today += 1
                logger.info(f"✅ Trade ejecutado - Señal: {signal}, Ticket: {ticket}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error al ejecutar trade: {str(e)}")
            return False

    def print_status(self):
        """Mostrar estado del bot y mercado con información de riesgo"""
        try:
            account_info = self.mt5.get_account_info()
            positions = self.order_manager.get_open_positions()
            
            logger.info("\n" + "=" * 50)
            logger.info("ESTADO DEL BOT")
            logger.info("=" * 50)
            logger.info(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Balance: ${account_info.get('balance', 'N/A'):.2f}")
            logger.info(f"Equity: ${account_info.get('equity', 'N/A'):.2f}")
            logger.info(f"Profit Actual: ${account_info.get('profit', 0):.2f}")
            logger.info(f"Posiciones Abiertas: {len(positions)}")
            logger.info(f"Trades Hoy: {self.trades_today}")
            
            if positions:
                logger.info("\nPosiciones Abiertas:")
                for pos in positions:
                    logger.info(f"  - {pos['type']} @ {pos['open_price']:.5f} | "
                              f"P/L: ${pos['profit']:.2f}")
            
            # Mostrar estado de riesgo
            self.risk_manager.print_risk_status()
            
            logger.info("=" * 50 + "\n")
            
        except Exception as e:
            logger.error(f"Error al mostrar estado: {str(e)}")

    def run(self, backtest_first: bool = True):
        """
        Ejecutar el bot de trading
        
        Args:
            backtest_first: Si True, ejecuta backtest antes de trading real
        """
        # Manejo de señales de interrupción
        def signal_handler(sig, frame):
            logger.info("\n⚠️ Señal de interrupción recibida. Deteniendo bot...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Inicializar
        if not self.initialize():
            logger.error("No se pudo inicializar el bot")
            return
        
        # Ejecutar backtest si se solicita
        if backtest_first:
            backtest_results = self.run_backtest(bars=500)
            
            # Validar resultados del backtest
            if backtest_results.get('win_rate', 0) < 45:
                logger.warning("⚠️ Win rate muy bajo en backtest. Considera ajustar parámetros.")
        
        self.running = True
        logger.info(f"🚀 Bot iniciado - Modo: {'REAL' if self.config['trading_enabled'] else 'DEMO'}")
        
        # Loop principal
        while self.running:
            try:
                # Mostrar estado
                self.print_status()
                
                # Verificar señal
                signal = self.check_signal()
                
                if signal:
                    logger.info(f"📊 Señal detectada: {signal}")
                    self.execute_trade(signal)
                
                # Esperar antes del siguiente ciclo
                wait_time = self.config["timeframe"] * 60  # Convertir a segundos
                logger.info(f"Esperando {wait_time}s hasta el siguiente ciclo...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("\n⚠️ Interrupción por usuario")
                break
            except Exception as e:
                logger.error(f"Error en loop principal: {str(e)}")
                time.sleep(60)
        
        # Cerrar conexión
        self.mt5.disconnect()
        logger.info("🛑 Bot detenido")


def main():
    """Función principal"""
    logger.info("=" * 50)
    logger.info("TRADING BOT RSI - XM Global MetaTrader 5")
    logger.info("=" * 50)
    logger.info("⚠️ DISCLAIMER: Este bot opera con dinero real.")
    logger.info("⚠️ Úsalo bajo tu propio riesgo.")
    logger.info("=" * 50)
    
    # Crear bot
    bot = TradingBot("config.json")
    
    # Ejecutar
    # Cambiar backtest_first=False si solo quieres trading sin validación
    bot.run(backtest_first=True)


if __name__ == "__main__":
    main()
