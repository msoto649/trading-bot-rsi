# 🤖 Trading Bot RSI - XM Global MetaTrader 5

Bot de trading automático con estrategia RSI (Relative Strength Index) + gestión inteligente de riesgo + backtesting + optimización de parámetros.

## ✨ Características Principales

### 1. **Estrategia RSI Avanzada**
- Indicador RSI con parámetros ajustables
- Señales de sobreventa/sobrecompra
- Integración con filtros de tendencia

### 2. **Backtesting Engine** 
- Valida estrategia con datos históricos (1-2 años)
- Calcula métricas: Win Rate, Profit Factor, Drawdown, Sharpe Ratio
- Exporta resultados en JSON

### 3. **Risk Management**
- Cálculo dinámico de lot size basado en riesgo
- Stop Loss y Take Profit ajustados por ATR
- Límites diarios de pérdida
- Escalado de posiciones según ganancias/pérdidas

### 4. **Signal Filters**
- Filtro de Tendencia (No operar contra tendencia)
- Filtro de Horas (Evita volatilidad baja)
- Filtro de Volatilidad (ATR)

### 5. **Parameter Optimization**
- Optimiza parámetros RSI automáticamente
- Genera top 10 mejores combinaciones

### 6. **Dashboard y Reporting**
- Monitoreo en tiempo real
- Métricas de performance
- Reportes HTML
- Exportación de datos

## 📁 Estructura del Proyecto

```
trading-bot-rsi/
├── src/
│   ├── __init__.py
│   ├── metatrader.py          # Conexión a MT5
│   ├── strategy.py             # Estrategia RSI
│   ├── orders.py               # Gestión de órdenes
│   ├── backtest_engine.py      # Motor de backtesting
│   ├── risk_manager.py         # Gestión de riesgo
│   ├── signal_filter.py        # Filtros de señal
│   ├── parameter_optimizer.py  # Optimización
│   ├── dashboard.py            # Dashboard y reportes
│   └── logger.py               # Sistema de logging
├── main.py                      # Archivo principal
├── config.json                  # Configuración
├── requirements.txt             # Dependencias
├── .gitignore
└── README.md
```

## 🚀 Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/msoto649/trading-bot-rsi.git
cd trading-bot-rsi

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
nano config.json
```

## ⚙️ Configuración

### config.json

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
  "max_positions": 1,
  "trading_enabled": false,
  "risk_per_trade": 2.0,
  "max_daily_loss": 5.0,
  "max_position_size": 0.5
}
```

## 📊 Uso

### Ejecutar Bot
```bash
python main.py
```

### Resultados Esperados
- Win Rate: > 55%
- Profit Factor: > 1.5
- Max Drawdown: < 15%

## ⚠️ DISCLAIMERS

- **NO hay garantía de ganancias** en trading
- **Riesgo de pérdida total del capital**
- **Usa solo dinero que puedas permitirte perder**
- **Prueba en DEMO mínimo 1 mes antes de real**

## 📞 Soporte

GitHub Issues: https://github.com/msoto649/trading-bot-rsi/issues

---

**Versión**: 2.0 (Con Risk Manager + Signal Filters + Optimizer)
**Última actualización**: 2026-06-16