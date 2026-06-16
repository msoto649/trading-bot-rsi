"""Módulo de Dashboard - Monitoreo en tiempo real"""

import logging
from datetime import datetime
from typing import Dict, List
import json

logger = logging.getLogger(__name__)


class Dashboard:
    """Clase para mostrar métricas en tiempo real"""

    def __init__(self):
        """Inicializar dashboard"""
        self.session_start = datetime.now()
        self.metrics_history = []
        logger.info("Dashboard inicializado")

    def record_metrics(self, metrics: Dict):
        """
        Registrar métricas en un momento específico
        
        Args:
            metrics: Diccionario con métricas
        """
        metrics["timestamp"] = datetime.now().isoformat()
        self.metrics_history.append(metrics)

    def display_trading_session_summary(self, bot_data: Dict):
        """
        Mostrar resumen de sesión de trading
        
        Args:
            bot_data: Datos del bot (balance, trades, etc.)
        """
        elapsed_time = datetime.now() - self.session_start
        hours = elapsed_time.total_seconds() // 3600
        minutes = (elapsed_time.total_seconds() % 3600) // 60
        
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DE SESIÓN DE TRADING")
        logger.info("=" * 60)
        logger.info(f"Tiempo de sesión: {int(hours)}h {int(minutes)}m")
        logger.info(f"Balance Inicial: ${bot_data.get('initial_balance', 'N/A'):.2f}")
        logger.info(f"Balance Actual: ${bot_data.get('current_balance', 'N/A'):.2f}")
        logger.info(f"Balance Ganancia: ${bot_data.get('balance_change', 0):.2f}")
        logger.info(f"Retorno %: {bot_data.get('return_percentage', 0):.2f}%")
        logger.info(f"\nOperaciones:")
        logger.info(f"  Total Trades: {bot_data.get('total_trades', 0)}")
        logger.info(f"  Trades Ganadores: {bot_data.get('winning_trades', 0)}")
        logger.info(f"  Trades Perdedores: {bot_data.get('losing_trades', 0)}")
        logger.info(f"  Win Rate: {bot_data.get('win_rate', 0):.2f}%")
        logger.info(f"\nRiesgo:")
        logger.info(f"  Posiciones Abiertas: {bot_data.get('open_positions', 0)}")
        logger.info(f"  Profit Actual: ${bot_data.get('current_profit', 0):.2f}")
        logger.info(f"  Drawdown: {bot_data.get('drawdown', 0):.2f}%")
        logger.info("=" * 60 + "\n")

    def display_performance_metrics(self, metrics: Dict):
        """
        Mostrar métricas de performance
        
        Args:
            metrics: Diccionario con métricas de performance
        """
        logger.info("\n" + "=" * 60)
        logger.info("MÉTRICAS DE PERFORMANCE")
        logger.info("=" * 60)
        logger.info(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        logger.info(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        logger.info(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        logger.info(f"Recovery Factor: {metrics.get('recovery_factor', 0):.2f}")
        logger.info(f"Avg Profit por Trade: ${metrics.get('avg_profit', 0):.2f}")
        logger.info(f"Max Profit: ${metrics.get('max_profit', 0):.2f}")
        logger.info(f"Max Loss: ${metrics.get('max_loss', 0):.2f}")
        logger.info("=" * 60 + "\n")

    def display_positions_detail(self, positions: List[Dict]):
        """
        Mostrar detalle de posiciones abiertas
        
        Args:
            positions: Lista de posiciones abiertas
        """
        if not positions:
            logger.info("No hay posiciones abiertas")
            return
        
        logger.info("\n" + "=" * 60)
        logger.info("POSICIONES ABIERTAS - DETALLE")
        logger.info("=" * 60)
        
        for i, pos in enumerate(positions, 1):
            logger.info(f"\nPosición {i}:")
            logger.info(f"  Ticket: {pos.get('ticket', 'N/A')}")
            logger.info(f"  Tipo: {pos.get('type', 'N/A')}")
            logger.info(f"  Precio Entrada: {pos.get('open_price', 0):.5f}")
            logger.info(f"  Precio Actual: {pos.get('current_price', 0):.5f}")
            logger.info(f"  Volumen: {pos.get('volume', 0)}")
            logger.info(f"  P/L: ${pos.get('profit', 0):.2f}")
            logger.info(f"  SL: {pos.get('sl', 0):.5f}")
            logger.info(f"  TP: {pos.get('tp', 0):.5f}")
        
        logger.info("=" * 60 + "\n")

    def display_trading_log(self, trades: List[Dict], limit: int = 10):
        """
        Mostrar log de últimos trades
        
        Args:
            trades: Lista de trades
            limit: Cantidad de trades a mostrar
        """
        if not trades:
            logger.info("No hay trades registrados")
            return
        
        logger.info("\n" + "=" * 60)
        logger.info(f"ÚLTIMOS {min(limit, len(trades))} TRADES")
        logger.info("=" * 60)
        
        for i, trade in enumerate(trades[-limit:], 1):
            logger.info(f"\nTrade {i}:")
            logger.info(f"  Tipo: {trade.get('type', 'N/A')}")
            logger.info(f"  Entrada: {trade.get('entry_price', 0):.5f}")
            logger.info(f"  Salida: {trade.get('exit_price', 0):.5f}")
            logger.info(f"  Ganancia: ${trade.get('profit', 0):.2f}")
            logger.info(f"  Razón: {trade.get('reason', 'N/A')}")
        
        logger.info("=" * 60 + "\n")

    def display_account_equity_curve(self, equity_history: List[float]):
        """
        Mostrar evolución de equity
        
        Args:
            equity_history: Lista de valores de equity
        """
        if not equity_history or len(equity_history) < 2:
            return
        
        initial = equity_history[0]
        current = equity_history[-1]
        max_equity = max(equity_history)
        min_equity = min(equity_history)
        
        change = ((current - initial) / initial) * 100 if initial > 0 else 0
        
        logger.info("\n" + "=" * 60)
        logger.info("CURVA DE EQUITY")
        logger.info("=" * 60)
        logger.info(f"Equity Inicial: ${initial:.2f}")
        logger.info(f"Equity Actual: ${current:.2f}")
        logger.info(f"Equity Máxima: ${max_equity:.2f}")
        logger.info(f"Equity Mínima: ${min_equity:.2f}")
        logger.info(f"Cambio: {change:.2f}%")
        logger.info("=" * 60 + "\n")

    def generate_html_report(self, filename: str, data: Dict):
        """
        Generar reporte HTML
        
        Args:
            filename: Nombre del archivo HTML
            data: Datos para el reporte
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-label {{ font-weight: bold; color: #2c3e50; }}
        .metric-value {{ font-size: 1.2em; color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; background-color: white; margin: 10px 0; }}
        th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Trading Bot Performance Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metric">
            <span class="metric-label">Balance Inicial:</span>
            <span class="metric-value">${data.get('initial_balance', 0):.2f}</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Balance Actual:</span>
            <span class="metric-value">${data.get('current_balance', 0):.2f}</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Ganancia/Pérdida:</span>
            <span class="metric-value {'negative' if data.get('balance_change', 0) < 0 else ''}">${data.get('balance_change', 0):.2f}</span>
        </div>
        
        <div class="metric">
            <span class="metric-label">Retorno %:</span>
            <span class="metric-value {'negative' if data.get('return_percentage', 0) < 0 else ''}">{data.get('return_percentage', 0):.2f}%</span>
        </div>
        
        <h2>Trading Statistics</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Total Trades</td>
                <td>{data.get('total_trades', 0)}</td>
            </tr>
            <tr>
                <td>Winning Trades</td>
                <td>{data.get('winning_trades', 0)}</td>
            </tr>
            <tr>
                <td>Losing Trades</td>
                <td>{data.get('losing_trades', 0)}</td>
            </tr>
            <tr>
                <td>Win Rate</td>
                <td>{data.get('win_rate', 0):.2f}%</td>
            </tr>
            <tr>
                <td>Profit Factor</td>
                <td>{data.get('profit_factor', 0):.2f}</td>
            </tr>
            <tr>
                <td>Max Drawdown</td>
                <td>{data.get('max_drawdown', 0):.2f}%</td>
            </tr>
        </table>
    </div>
</body>
</html>
            """
            
            with open(filename, 'w') as f:
                f.write(html_content)
            
            logger.info(f"Reporte HTML generado: {filename}")
            
        except Exception as e:
            logger.error(f"Error al generar reporte HTML: {str(e)}")

    def export_metrics_to_json(self, filename: str = None):
        """Exportar métricas a JSON"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
            logger.info(f"Métricas exportadas a {filename}")
        except Exception as e:
            logger.error(f"Error al exportar métricas: {str(e)}")
