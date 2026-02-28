"""
Trading Monitor - Configuration System
Supports demo/real account switching with a single flag change.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".trading_monitor"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class AccountConfig:
    """MT5 account credentials."""
    server: str = ""
    login: int = 0
    password: str = ""
    label: str = ""  # "demo" or "real"


@dataclass
class KillSwitchConfig:
    """Kill switch thresholds - calibrated for ~660 EUR account."""
    max_daily_loss_pct: float = 3.0        # ~20 EUR/day max loss
    max_total_drawdown_pct: float = 10.0   # ~66 EUR max drawdown total
    max_open_positions: int = 5            # conservative for small account
    max_lot_size: float = 0.10             # max 0.10 lots per position
    max_total_exposure: float = 0.30       # max 0.30 lots total
    pause_after_consecutive_losses: int = 3
    enabled: bool = True


@dataclass
class DashboardConfig:
    """Dashboard display settings."""
    refresh_interval_sec: int = 5
    show_closed_trades: int = 10   # last N closed trades
    currency: str = "EUR"
    timezone: str = "America/Sao_Paulo"


@dataclass
class ZuluTradeConfig:
    """ZuluTrade integration settings."""
    followed_traders: list = field(default_factory=list)
    zuluguard_enabled: bool = True
    zuluguard_max_loss_per_trader: float = 50.0  # EUR - conservative for 660 EUR account


@dataclass
class Config:
    """Master configuration."""
    # Which account to use: "demo" or "real"
    active_mode: str = "real"

    # Account credentials
    demo_account: AccountConfig = field(default_factory=lambda: AccountConfig(
        server="ActivTrades-Demo",
        login=0,
        password="",
        label="demo"
    ))
    real_account: AccountConfig = field(default_factory=lambda: AccountConfig(
        server="ActivTrades-Server",
        login=958831,
        password="",  # Set via: trading-monitor setup (stored in ~/.trading_monitor/config.json)
        label="real"
    ))

    # Sub-configs
    kill_switch: KillSwitchConfig = field(default_factory=KillSwitchConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    zulutrade: ZuluTradeConfig = field(default_factory=ZuluTradeConfig)

    @property
    def active_account(self) -> AccountConfig:
        """Returns the currently active account config."""
        if self.active_mode == "real":
            return self.real_account
        return self.demo_account

    def switch_to_real(self):
        """Switch from demo to real account."""
        self.active_mode = "real"
        self.save()

    def switch_to_demo(self):
        """Switch from real to demo account."""
        self.active_mode = "demo"
        self.save()

    def save(self):
        """Persist config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls) -> "Config":
        """Load config from disk, or create default."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            cfg = cls()
            cfg.active_mode = data.get("active_mode", "demo")
            demo = data.get("demo_account", {})
            cfg.demo_account = AccountConfig(**demo)
            real = data.get("real_account", {})
            cfg.real_account = AccountConfig(**real)
            ks = data.get("kill_switch", {})
            cfg.kill_switch = KillSwitchConfig(**ks)
            dash = data.get("dashboard", {})
            cfg.dashboard = DashboardConfig(**dash)
            zt = data.get("zulutrade", {})
            if "followed_traders" in zt:
                zt["followed_traders"] = zt["followed_traders"]
            cfg.zulutrade = ZuluTradeConfig(**zt)
            return cfg
        else:
            cfg = cls()
            cfg.save()
            return cfg


def setup_wizard():
    """Interactive setup for first-time configuration."""
    print("\n=== Trading Monitor - Setup ===\n")
    cfg = Config()

    print("[1/4] Demo Account (ActivTrades)")
    cfg.demo_account.server = input("  Server (ActivTrades-Demo): ").strip() or "ActivTrades-Demo"
    login = input("  Login (account number): ").strip()
    cfg.demo_account.login = int(login) if login else 0
    cfg.demo_account.password = input("  Password: ").strip()
    cfg.demo_account.label = "demo"

    print("\n[2/4] Real Account (pre-configure for later)")
    cfg.real_account.server = input("  Server (ActivTrades-Server): ").strip() or "ActivTrades-Server"
    login = input("  Login (account number, or 0 to skip): ").strip()
    cfg.real_account.login = int(login) if login else 0
    cfg.real_account.password = input("  Password (or empty to skip): ").strip()
    cfg.real_account.label = "real"

    print("\n[3/4] Kill Switch Limits")
    val = input(f"  Max daily loss % [{cfg.kill_switch.max_daily_loss_pct}]: ").strip()
    if val:
        cfg.kill_switch.max_daily_loss_pct = float(val)
    val = input(f"  Max total drawdown % [{cfg.kill_switch.max_total_drawdown_pct}]: ").strip()
    if val:
        cfg.kill_switch.max_total_drawdown_pct = float(val)
    val = input(f"  Max open positions [{cfg.kill_switch.max_open_positions}]: ").strip()
    if val:
        cfg.kill_switch.max_open_positions = int(val)

    print("\n[4/4] Dashboard")
    val = input(f"  Refresh interval seconds [{cfg.dashboard.refresh_interval_sec}]: ").strip()
    if val:
        cfg.dashboard.refresh_interval_sec = int(val)

    cfg.active_mode = "demo"
    cfg.save()
    print(f"\nConfig saved to {CONFIG_FILE}")
    print("Starting in DEMO mode. Use 'trading-monitor switch real' when ready.\n")
    return cfg
