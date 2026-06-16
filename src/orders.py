"""Módulo de gestión de órdenes - Order Manager"""

import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class OrderManager:
    """Clase para gestionar órdenes de trading"""

    def __init__(self, symbol: str, lot_size: float, stop_loss_pips: float, take_profit_pips: float):
        """
        Inicializar gestor de órdenes
        
        Args:
            symbol: Símbolo a tradear (e.g., 'EU50')
            lot_size: Tamaño del lote
            stop_loss_pips: Stop loss en pips
            take_profit_pips: Take profit en pips
        """
        self.symbol = symbol
        self.lot_size = lot_size
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.open_positions = []
        self.closed_trades = []
        logger.info(f"OrderManager inicializado - Symbol: {symbol}, Lot: {lot_size}")

    def send_order(self, order_type: str, entry_price: float) -> Optional[int]:
        """
        Enviar orden de compra/venta
        
        Args:
            order_type: 'BUY' o 'SELL'
            entry_price: Precio de entrada
            
        Returns:
            int: Número de ticket o None si falla
        """
        try:
            # Calcular SL y TP
            if order_type == "BUY":
                sl_price = entry_price - (self.stop_loss_pips * 0.0001)
                tp_price = entry_price + (self.take_profit_pips * 0.0001)
            else:  # SELL
                sl_price = entry_price + (self.stop_loss_pips * 0.0001)
                tp_price = entry_price - (self.take_profit_pips * 0.0001)
            
            # Crear posición simulada
            ticket = len(self.open_positions) + 1
            position = {
                "ticket": ticket,
                "type": order_type,
                "open_price": entry_price,
                "current_price": entry_price,
                "volume": self.lot_size,
                "sl": sl_price,
                "tp": tp_price,
                "profit": 0.0
            }
            
            self.open_positions.append(position)
            logger.info(f"Orden {order_type} enviada - Ticket: {ticket}, Precio: {entry_price:.5f}, SL: {sl_price:.5f}, TP: {tp_price:.5f}")
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error al enviar orden: {str(e)}")
            return None

    def get_open_positions(self) -> List[Dict]:
        """
        Obtener posiciones abiertas
        
        Returns:
            list: Lista de posiciones abiertas
        """
        return self.open_positions

    def close_position(self, ticket: int, exit_price: float, reason: str = "Manual") -> bool:
        """
        Cerrar una posición
        
        Args:
            ticket: Número de ticket
            exit_price: Precio de salida
            reason: Razón del cierre
            
        Returns:
            bool: True si se cerró exitosamente
        """
        try:
            for pos in self.open_positions:
                if pos["ticket"] == ticket:
                    # Calcular ganancia/pérdida
                    if pos["type"] == "BUY":
                        profit = (exit_price - pos["open_price"]) * pos["volume"] * 10000
                    else:
                        profit = (pos["open_price"] - exit_price) * pos["volume"] * 10000
                    
                    # Registrar trade cerrado
                    closed_trade = {
                        "ticket": ticket,
                        "type": pos["type"],
                        "entry_price": pos["open_price"],
                        "exit_price": exit_price,
                        "volume": pos["volume"],
                        "profit": profit,
                        "reason": reason
                    }
                    
                    self.closed_trades.append(closed_trade)
                    self.open_positions.remove(pos)
                    
                    logger.info(f"Posición {ticket} cerrada - Ganancia: ${profit:.2f} - Razón: {reason}")
                    return True
            
            logger.warning(f"Posición {ticket} no encontrada")
            return False
            
        except Exception as e:
            logger.error(f"Error al cerrar posición: {str(e)}")
            return False

    def update_position_price(self, ticket: int, current_price: float) -> bool:
        """
        Actualizar precio actual de una posición
        
        Args:
            ticket: Número de ticket
            current_price: Precio actual
            
        Returns:
            bool: True si se actualizó
        """
        try:
            for pos in self.open_positions:
                if pos["ticket"] == ticket:
                    pos["current_price"] = current_price
                    
                    # Calcular profit actual
                    if pos["type"] == "BUY":
                        pos["profit"] = (current_price - pos["open_price"]) * pos["volume"] * 10000
                    else:
                        pos["profit"] = (pos["open_price"] - current_price) * pos["volume"] * 10000
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error al actualizar posición: {str(e)}")
            return False

    def check_sl_tp(self) -> List[Dict]:
        """
        Verificar si alguna posición debe ser cerrada por SL o TP
        
        Returns:
            list: Posiciones que alcanzaron SL o TP
        """
        positions_to_close = []
        
        try:
            for pos in self.open_positions:
                should_close = False
                reason = ""
                
                if pos["type"] == "BUY":
                    if pos["current_price"] >= pos["tp"]:
                        should_close = True
                        reason = "Take Profit"
                    elif pos["current_price"] <= pos["sl"]:
                        should_close = True
                        reason = "Stop Loss"
                
                elif pos["type"] == "SELL":
                    if pos["current_price"] <= pos["tp"]:
                        should_close = True
                        reason = "Take Profit"
                    elif pos["current_price"] >= pos["sl"]:
                        should_close = True
                        reason = "Stop Loss"
                
                if should_close:
                    positions_to_close.append({
                        "ticket": pos["ticket"],
                        "reason": reason,
                        "exit_price": pos["tp"] if "Profit" in reason else pos["sl"]
                    })
            
            return positions_to_close
            
        except Exception as e:
            logger.error(f"Error al verificar SL/TP: {str(e)}")
            return []

    def get_closed_trades(self) -> List[Dict]:
        """
        Obtener trades cerrados
        
        Returns:
            list: Lista de trades cerrados
        """
        return self.closed_trades

    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas de trading
        
        Returns:
            dict: Estadísticas
        """
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_profit": 0,
                "avg_profit": 0
            }
        
        winning = [t for t in self.closed_trades if t["profit"] > 0]
        losing = [t for t in self.closed_trades if t["profit"] <= 0]
        total_profit = sum(t["profit"] for t in self.closed_trades)
        
        return {
            "total_trades": len(self.closed_trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": (len(winning) / len(self.closed_trades) * 100) if self.closed_trades else 0,
            "total_profit": total_profit,
            "avg_profit": total_profit / len(self.closed_trades) if self.closed_trades else 0
        }

    def reset(self):
        """Resetear todas las posiciones"""
        self.open_positions = []
        self.closed_trades = []
        logger.info("OrderManager reseteado")
