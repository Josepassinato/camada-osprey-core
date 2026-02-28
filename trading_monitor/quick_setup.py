#!/usr/bin/env python3
"""
Quick Setup - Configura conta real ActivTrades #958831
Só precisa digitar a senha MT5.
"""

import getpass
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".trading_monitor"
CONFIG_FILE = CONFIG_DIR / "config.json"


def main():
    print()
    print("=" * 50)
    print("  TRADING MONITOR - Setup Rápido")
    print("  Conta: ActivTrades #958831 (REAL)")
    print("  Balance: 657.68 EUR")
    print("=" * 50)
    print()

    # Ask for password securely (hidden input)
    password = getpass.getpass("  Digite sua senha MT5 (ActivTrades): ")

    if not password:
        print("\n  Senha vazia. Abortado.")
        return

    config = {
        "active_mode": "real",
        "demo_account": {
            "server": "ActivTrades-Demo",
            "login": 0,
            "password": "",
            "label": "demo"
        },
        "real_account": {
            "server": "ActivTrades-Server",
            "login": 958831,
            "password": password,
            "label": "real"
        },
        "kill_switch": {
            "max_daily_loss_pct": 3.0,
            "max_total_drawdown_pct": 10.0,
            "max_open_positions": 5,
            "max_lot_size": 0.10,
            "max_total_exposure": 0.30,
            "pause_after_consecutive_losses": 3,
            "enabled": True
        },
        "dashboard": {
            "refresh_interval_sec": 5,
            "show_closed_trades": 10,
            "currency": "EUR",
            "timezone": "America/Sao_Paulo"
        },
        "zulutrade": {
            "followed_traders": [],
            "zuluguard_enabled": True,
            "zuluguard_max_loss_per_trader": 50.0
        }
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    # Protect config file (owner read/write only)
    CONFIG_FILE.chmod(0o600)

    print()
    print(f"  Config salva em: {CONFIG_FILE}")
    print(f"  Permissões: 600 (só você pode ler)")
    print()
    print("  Configuração:")
    print(f"    Modo:           REAL")
    print(f"    Server:         ActivTrades-Server")
    print(f"    Login:          958831")
    print(f"    Currency:       EUR")
    print(f"    Kill Switch:    ON")
    print(f"    Daily Loss Max: 3% (~20 EUR)")
    print(f"    Drawdown Max:   10% (~66 EUR)")
    print(f"    Max Positions:  5")
    print(f"    Max Lot/Trade:  0.10")
    print(f"    Max Exposure:   0.30 lots")
    print()
    print("  Próximos passos:")
    print("    1. python -m trading_monitor.main sim       # Testar dashboard")
    print("    2. python -m trading_monitor.main monitor   # Monitorar (Windows+MT5)")
    print("    3. python -m trading_monitor.main status    # Ver status rápido")
    print()


if __name__ == "__main__":
    main()
