"""
Trading Monitor - Web Dashboard API
FastAPI backend with WebSocket for real-time trading data.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from ..config import Config
from ..mt5_client import MT5Client, MT5_AVAILABLE

logger = logging.getLogger("trading_monitor.web")

app = FastAPI(title="Trading Monitor", version="1.0.0")

# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Global state
_config: Optional[Config] = None
_client: Optional[MT5Client] = None
_metaapi_account = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def get_simulated_data() -> dict:
    """Return simulated account data matching ActivTrades #958831."""
    config = get_config()
    now = datetime.now()
    base_balance = 657.68

    # Slight variations to simulate real-time changes
    import random
    tick = random.uniform(-2, 3)

    return {
        "account": {
            "login": config.active_account.login or 958831,
            "server": config.active_account.server or "ActivTrades-Server",
            "balance": base_balance,
            "equity": round(base_balance + tick, 2),
            "profit": round(tick, 2),
            "margin": 12.50,
            "free_margin": round(base_balance + tick - 12.50, 2),
            "margin_level": round(((base_balance + tick) / 12.50) * 100, 1) if 12.50 > 0 else 0,
            "currency": "EUR",
            "leverage": 400,
            "name": "CARMARGO PASSINATO",
            "company": "ActivTrades Plc",
        },
        "positions": [
            {
                "ticket": 200001,
                "symbol": "EURUSD",
                "type": "buy",
                "volume": 0.02,
                "open_price": 1.08450,
                "current_price": round(1.08450 + random.uniform(-0.0010, 0.0015), 5),
                "profit": round(random.uniform(-1.5, 3.0), 2),
                "swap": -0.10,
                "sl": 1.08200,
                "tp": 1.08800,
                "open_time": now.strftime("%H:%M"),
                "magic": 10001,
            },
            {
                "ticket": 200002,
                "symbol": "XAUUSD",
                "type": "buy",
                "volume": 0.01,
                "open_price": 2650.50,
                "current_price": round(2650.50 + random.uniform(-3, 8), 2),
                "profit": round(random.uniform(-1.0, 4.0), 2),
                "swap": -0.30,
                "sl": 2640.00,
                "tp": 2670.00,
                "open_time": now.strftime("%H:%M"),
                "magic": 10002,
            },
        ],
        "kill_switch": {
            "enabled": True,
            "paused": False,
            "daily_loss_pct": round(abs(tick) / base_balance * 100, 2) if tick < 0 else 0,
            "daily_loss_limit": 3.0,
            "drawdown_pct": 0.0,
            "drawdown_limit": 10.0,
            "open_positions": 2,
            "max_positions": 5,
            "total_exposure": 0.03,
            "max_exposure": 0.30,
        },
        "daily_pnl": round(tick, 2),
        "mode": config.active_mode.upper(),
        "timestamp": now.strftime("%H:%M:%S"),
        "connected": True,
        "data_source": "simulation",
    }


def get_live_data() -> dict:
    """Get real data from MT5 or MetaAPI."""
    global _client
    config = get_config()

    if MT5_AVAILABLE and _client and _client.connected:
        info = _client.get_account_info()
        positions = _client.get_positions()
        if info:
            return {
                "account": {
                    "login": info.login,
                    "server": info.server,
                    "balance": info.balance,
                    "equity": info.equity,
                    "profit": info.profit,
                    "margin": info.margin,
                    "free_margin": info.free_margin,
                    "margin_level": info.margin_level,
                    "currency": info.currency,
                    "leverage": info.leverage,
                    "name": info.name,
                    "company": info.company,
                },
                "positions": [
                    {
                        "ticket": p.ticket,
                        "symbol": p.symbol,
                        "type": p.type,
                        "volume": p.volume,
                        "open_price": p.open_price,
                        "current_price": p.current_price,
                        "profit": p.profit,
                        "swap": p.swap,
                        "sl": p.sl,
                        "tp": p.tp,
                        "open_time": p.open_time.strftime("%H:%M"),
                        "magic": p.magic,
                    }
                    for p in positions
                ],
                "kill_switch": {
                    "enabled": config.kill_switch.enabled,
                    "paused": False,
                    "daily_loss_pct": _client.get_daily_loss_pct(),
                    "daily_loss_limit": config.kill_switch.max_daily_loss_pct,
                    "drawdown_pct": _client.get_total_drawdown_pct(),
                    "drawdown_limit": config.kill_switch.max_total_drawdown_pct,
                    "open_positions": len(positions),
                    "max_positions": config.kill_switch.max_open_positions,
                    "total_exposure": sum(p.volume for p in positions),
                    "max_exposure": config.kill_switch.max_total_exposure,
                },
                "daily_pnl": _client.get_daily_pnl(),
                "mode": config.active_mode.upper(),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "connected": True,
                "data_source": "mt5",
            }

    return get_simulated_data()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard HTML."""
    html_path = STATIC_DIR / "index.html"
    return FileResponse(str(html_path))


@app.get("/api/data")
async def api_data():
    """REST endpoint for current data."""
    return get_live_data()


@app.get("/api/config")
async def api_config():
    """Get current configuration."""
    config = get_config()
    return {
        "mode": config.active_mode,
        "account_login": config.active_account.login,
        "server": config.active_account.server,
        "kill_switch": {
            "enabled": config.kill_switch.enabled,
            "max_daily_loss_pct": config.kill_switch.max_daily_loss_pct,
            "max_total_drawdown_pct": config.kill_switch.max_total_drawdown_pct,
            "max_open_positions": config.kill_switch.max_open_positions,
            "max_lot_size": config.kill_switch.max_lot_size,
            "max_total_exposure": config.kill_switch.max_total_exposure,
        },
        "currency": config.dashboard.currency,
    }


@app.post("/api/kill")
async def api_kill():
    """Emergency close all positions."""
    if _client and _client.connected:
        results = _client.close_all_positions()
        return {"action": "kill", "results": results}
    return {"action": "kill", "error": "Not connected to MT5"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time data streaming."""
    await websocket.accept()
    try:
        while True:
            data = get_live_data()
            await websocket.send_json(data)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the web dashboard server."""
    import uvicorn
    print(f"\n  Trading Monitor Web Dashboard")
    print(f"  Open in browser: http://localhost:{port}")
    print(f"  On phone (same network): http://<your-ip>:{port}")
    print(f"  Press Ctrl+C to stop\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
