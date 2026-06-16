# Trading Bot RSI - XM Global MetaTrader 5

Bot de trading automático para operar índices en XM Global mediante MetaTrader 5, utilizando la estrategia RSI (Relative Strength Index).

## 📋 Características

- ✅ Conexión automática a MetaTrader 5
- ✅ Estrategia RSI customizable
- ✅ Gestión automática de órdenes (BUY/SELL)
- ✅ Stop Loss y Take Profit
- ✅ Logging completo de operaciones
- ✅ Soporte para múltiples índices
- ✅ Configuración flexible

## 📊 Estrategia RSI

- **Señal de COMPRA**: RSI < 30 (Sobreventa)
- **Señal de VENTA**: RSI > 70 (Sobrecompra)
- **Periodo RSI**: 14 (configurable)

## 🚀 Inicio Rápido

### Requisitos

- Python 3.8 o superior
- MetaTrader 5 instalado
- Cuenta de XM Global

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/msoto649/trading-bot-rsi.git
cd trading-bot-rsi

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

1. Editar `config.json` con tus datos:

```json
{
  "account_number": "TU_NUMERO_DE_CUENTA",
  "password": "TU_PASSWORD",
  "server": "XMGlobal-MT5",
  "symbol": "EU50",
  "timeframe": 15,
  "rsi_period": 14,
  "rsi_overbought": 70,
  "rsi_oversold": 30,
  "lot_size": 0.1,
  "stop_loss_pips": 50,
  "take_profit_pips": 100,
  "trading_enabled": false
}
```

2. Ejecutar el bot:

```bash
python main.py
```

## 📁 Estructura del Proyecto

```
trading-bot-rsi/
├── main.py                 # Archivo principal
├── config.json            # Configuración del bot
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── .gitignore            # Archivos a ignorar
├── logs/                 # Logs de operaciones
└── src/
    ├── __init__.py
    ├── metatrader.py    # Conexión a MT5
    ├── strategy.py      # Estrategia RSI
    ├── orders.py        # Gestión de órdenes
    └── logger.py        # Sistema de logging
```

## ⚙️ Configuración Detallada

### Parámetros principales

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `account_number` | Número de cuenta MT5 | - |
| `password` | Contraseña MT5 | - |
| `symbol` | Símbolo a operar | EU50 |
| `timeframe` | Timeframe en minutos | 15 |
| `rsi_period` | Período del RSI | 14 |
| `rsi_overbought` | Nivel de sobrecompra | 70 |
| `rsi_oversold` | Nivel de sobreventa | 30 |
| `lot_size` | Tamaño del lote | 0.1 |
| `stop_loss_pips` | Stop Loss en pips | 50 |
| `take_profit_pips` | Take Profit en pips | 100 |
| `trading_enabled` | Habilitar trading real | false |

## 📊 Símbolos Soportados

- EU50 (STOXX Europe 50)
- GER40 (DAX)
- SPX500 (S&P 500)
- UK100 (FTSE 100)
- FRA40 (CAC 40)
- Otros índices disponibles en XM Global

## 📝 Logging

Todas las operaciones se registran en:
- `logs/trading_log_YYYYMMDD.log` - Log de todas las transacciones
- `logs/errors_YYYYMMDD.log` - Log de errores

## ⚠️ Disclaimer

**IMPORTANTE**: Este bot opera con dinero real. Úsalo bajo tu propio riesgo:

- ⚠️ Comienza con pequeños lotes para testing
- ⚠️ Revisa el logging regularmente
- ⚠️ No uses dinero que no puedas perder
- ⚠️ Monitorea el bot regularmente
- ⚠️ Prueba primero en cuenta demo
- ⚠️ No existe garantía de ganancias

## 🔧 Troubleshooting

### Error: "No se puede conectar a MT5"
- Verifica que MetaTrader 5 esté abierto
- Comprueba que estés conectado a la cuenta correcta
- Verifica el servidor configurado en config.json

### Error: "Orden rechazada"
- Verifica el balance disponible
- Comprueba el símbolo y spread
- Revisa el horario de mercado
- Asegúrate que `trading_enabled` sea `true`

### Error: "Módulo no encontrado"
```bash
pip install -r requirements.txt
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto está bajo la licencia MIT.

## 📧 Contacto

Para preguntas o sugerencias, abre un GitHub Issue.