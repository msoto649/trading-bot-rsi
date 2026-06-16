"""Módulo de logging"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Configurar sistema de logging
    
    Args:
        log_dir: Directorio para almacenar logs
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear directorio si no existe
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Crear logger
    logger = logging.getLogger("TradingBot")
    logger.setLevel(logging.DEBUG)
    
    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo de log general
    log_file = os.path.join(log_dir, f"trading_log_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para archivo de errores
    error_file = os.path.join(log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info("Sistema de logging inicializado")
    
    return logger
