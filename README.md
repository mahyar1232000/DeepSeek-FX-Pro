# ---------- README.md ----------

# DeepSeek-FX-Pro

**AI-Powered Multi-Timeframe Forex Trading System with MetaTrader 5**

## Features

- Multi-Timeframe Forecasting (LSTM + Ensemble Blending)
- Strategy Generation with Risk Evaluation
- Broker Integration (MetaTrader 5)
- Real-Time Trade Execution & Logging
- Secure Credential Management
- Configurable Hyperparameter Tuning
- Live & Backtest Support

## Project Structure

```
DeepSeek-FX-Pro/
├── ai_engine/
│   ├── StrategyGenerator.py
│   ├── RiskEvaluator.py
│   ├── ForecastModule.py
│   └── ModelUpdater.py
├── broker_interface/
│   ├── MT5Controller.py
│   ├── DataFeed.py
│   └── OrderManager.py
├── config/
│   ├── credentials.enc
│   ├── risk_params.json
│   ├── symbol_list.json
│   ├── config.yaml
│   └── key.key
├── core/
│   ├── PortfolioManager.py
│   ├── PerformanceTracker.py
│   ├── OrderExecutor.py
│   ├── AlertSystem.py
│   └── TradingEngine.py
├── utils/
│   ├── AdvancedLogger.py
│   ├── DataPreprocessor.py
│   ├── ReportGenerator.py
│   ├── SecurityModule.py
│   └── mt5_data.py
├── models/
├── requirements.txt
├── setup.py
├── main.py
└── README.md
```

## Getting Started

1. Clone the repo:

```bash
git clone https://github.com/mahyar1232000/DeepSeek-FX-Pro.git
cd DeepSeek-FX-Pro
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add encrypted credentials:

```bash
python -m utils.SecurityModule generate_key
# Then encrypt config/credentials.json to config/credentials.enc
```

4. Configure parameters in `config/config.yaml`

5. Run the bot:

```bash
python main.py
```

## License

MIT License
