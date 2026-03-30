# 360-Crypto-Scalping V2 — AI-Powered Futures Scalping Engine

A high-performance asynchronous Python engine that scans the **top 50 USDT-M futures pairs** on Binance in real-time, detects Smart Money Concepts (SMC) setups, calculates dynamic confidence scores (0–100), and routes signals to a **single Active Trading** Telegram channel.

## Architecture

```
Binance REST ──► PairManager (top 50 futures, auto-refresh)
                       │
                       ▼
              HistoricalDataStore (OHLCV seed per timeframe)
                       │
Binance WS ──► WebSocketManager (multi-conn, heartbeat, auto-reconnect)
                       │
                       ▼
                  Scanner Loop
           ┌───────────┤────────────┐
     Indicators    SMC Algos    AI Engine
           └───────────┤────────────┘
                       ▼
                 Scalp Strategies
       (SCALP · FVG · CVD · VWAP · OBI)
                       │
               ConfidenceScorer (0–100)
                       │
                 asyncio.Queue
                       │
                       ▼
                 SignalRouter ──► Telegram
                       │             └─ ⚡ Active Trading
                       ▼
                 TradeMonitor
           (TP/SL · Trailing · Updates)
                       │
           ┌───────────┼───────────────┐
     PerformanceTracker          CircuitBreaker
     (real stats)                (auto-pause)
```

## Key Design Decisions

- **Single Channel** — All signals go to one **Active Trading** channel. No separate portfolio channels (gem, spot, swing). Simpler for users, easier to maintain.
- **Top-50 Futures Only** — Scans the top 50 USDT-M futures by 24h volume. Reduces API weight, memory, and scan latency vs. scanning 800+ pairs.
- **Docker-First** — One-click VPS deployment with Docker Compose. No manual Python/venv setup needed.

## Features

| Feature | Module | Description |
|---|---|---|
| **SMC Detection** | `src/smc.py` | Liquidity Sweeps, Market Structure Shifts (MSS), Fair Value Gaps (FVG) |
| **5 Scalp Strategies** | `src/channels/` | Standard Scalp, FVG, CVD, VWAP Deviation, Order Book Imbalance |
| **AI Sentiment** | `src/ai_engine.py` | CryptoPanic news, LunarCrush social, Fear & Greed Index |
| **Confidence Scoring** | `src/confidence.py` | Multi-layer 0–100 with 7 sub-components |
| **Dynamic Pairs** | `src/pair_manager.py` | Auto-fetch top 50 futures, prune stale pairs |
| **WebSocket Resilience** | `src/websocket_manager.py` | Multi-connection, heartbeat, exponential-backoff reconnect |
| **Trade Monitoring** | `src/trade_monitor.py` | Real-time TP/SL tracking, trailing stops, PnL updates |
| **Telemetry** | `src/telemetry.py` | CPU, memory, WS health, scan latency, API usage |
| **Circuit Breaker** | `src/circuit_breaker.py` | Auto-pauses after consecutive losses |
| **Performance Tracker** | `src/performance_tracker.py` | Win rates, TP hit rates, signal quality scoring |
| **Predictive AI** | `src/predictive_ai.py` | ML-based price direction prediction |
| **Market Regime** | `src/regime.py` | Trending / ranging / volatile classification |
| **Redis Caching** | `src/redis_client.py` | Optional Redis-backed signal state persistence |
| **Admin Commands** | `src/commands/` | Full Telegram admin & user command suite |

## One-Click VPS Deployment

Deploy on a fresh Ubuntu VPS (20.04 / 22.04 / 24.04) with a single command:

```bash
git clone https://github.com/mkmk749278/360-v2.git && cd 360-v2
cp .env.example .env
nano .env              # Fill in your Telegram credentials
sudo bash deploy_vps.sh
```

That's it. The script installs Docker, builds the image, starts Redis + Engine.

### What `deploy_vps.sh` does

1. Installs Docker & Docker Compose (if not present)
2. Clones/updates the repository
3. Creates `.env` from `.env.example`
4. Builds the Docker image
5. Starts Redis + Engine with `docker compose up -d`
6. Prints management commands

### Service Management

```bash
docker compose logs -f engine      # Follow live logs
docker compose restart engine      # Restart the engine
docker compose down                # Stop everything
docker compose up -d --build       # Rebuild and restart
docker compose ps                  # Check status
sudo bash deploy_vps.sh --clean    # Full cleanup and redeploy
```

## Configuration

Edit `.env` before deploying. Required variables:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_ACTIVE_CHANNEL_ID` | Active Trading channel ID |
| `TELEGRAM_ADMIN_CHAT_ID` | Your personal chat ID for admin commands |

Optional AI APIs (engine works without them, capped at ~85% confidence):

| Variable | Service | Free? |
|---|---|---|
| `NEWS_API_KEY` | CryptoPanic news sentiment | Yes |
| `SOCIAL_SENTIMENT_API_KEY` | LunarCrush social sentiment | Yes |
| `OPENAI_API_KEY` | GPT-4 macro evaluator | No |
| `ONCHAIN_API_KEY` | Glassnode on-chain data | No |

## Telegram Commands

### Admin Commands

| Command | Description |
|---|---|
| `/status` | Engine uptime, tasks, queue, WS health |
| `/view_dashboard` | Full telemetry dashboard |
| `/update_pairs` | Refresh top-50 futures pairs |
| `/force_scan` | Trigger immediate scanner cycle |
| `/view_pairs` | View active pairs by volume |
| `/view_active_signals` | List all active signals |
| `/view_logs [lines]` | View recent log output |
| `/stats` | Performance statistics |
| `/real_stats` | Real signal outcome stats |
| `/circuit_breaker_status` | Circuit breaker state |
| `/reset_circuit_breaker` | Reset circuit breaker |
| `/restart_engine` | Restart all engine tasks |
| `/update_code` | Run `git pull` on the server |
| `/memory_usage` | Show RSS, VMS, CPU usage |

### User Commands

| Command | Description |
|---|---|
| `/signals` | Show last 5 active signals |
| `/signal_info <id>` | Detailed info on a specific signal |
| `/last_update` | Last scan latency & pair count |
| `/signal_history` | Last 10 completed signals |
| `/signal_stats` | Signal quality statistics |
| `/tp_stats` | TP hit rate statistics |

## Signal Format

```
⚡ SCALP ALERT 💎
Pair: BTCUSDT (Futures)
📈 LONG 🚀
🚀 Entry: 68,150
🛡️ SL: 68,080
🎯 TP1: 68,250 (1R)
🎯 TP2: 68,350 (1.5R)
🎯 TP3: 68,500 (2R)
💹 Trailing: 1.5×ATR
🤖 Confidence: 87%
📰 AI: Bullish — Whale accumulation detected
⚠️ Risk: Moderate
```

## Project Structure

```
config/
  __init__.py              # All settings, channel configs, constants
src/
  main.py                  # Engine orchestrator & entry point
  bootstrap.py             # Boot sequence, WS initialisation
  scanner/                 # Core scanning loop
  channels/
    base.py                # Signal model & base strategy
    scalp.py               # Standard scalp (M1/M5)
    scalp_fvg.py           # Fair Value Gap scalp
    scalp_cvd.py           # CVD divergence scalp
    scalp_vwap.py          # VWAP deviation scalp
    scalp_obi.py           # Order Book Imbalance scalp
  indicators.py            # EMA, SMA, ADX, ATR, RSI, Bollinger
  smc.py                   # Liquidity Sweep, MSS, FVG detection
  confidence.py            # Multi-layer confidence scorer (0–100)
  ai_engine.py             # News/social sentiment, whale detection
  pair_manager.py          # Dynamic top-50 pair management
  historical_data.py       # OHLCV & tick seeding
  websocket_manager.py     # Multi-connection WS with resilience
  signal_router.py         # Queue-based signal dispatch
  signal_queue.py          # Async signal queue (Redis fallback)
  trade_monitor.py         # TP/SL/trailing monitoring
  telegram_bot.py          # Signal formatting & Telegram commands
  commands/                # Telegram command handlers
  telemetry.py             # System health monitoring
  circuit_breaker.py       # Auto-pause after consecutive losses
  performance_tracker.py   # Signal outcome tracking
  predictive_ai.py         # ML price direction prediction
  regime.py                # Market regime classification
  risk.py                  # Position sizing & risk enforcement
  filters.py               # Pre-signal filters
  exchange.py              # Unified exchange interface
  binance.py               # Binance REST/WS API client
  redis_client.py          # Redis caching layer
tests/
  test_indicators.py
  test_smc.py
  test_confidence.py
  test_channels.py
  test_signal_router.py
  test_telegram_format.py
```

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```