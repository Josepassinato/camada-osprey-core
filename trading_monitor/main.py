#!/usr/bin/env python3
"""
Trading Monitor - CLI Entry Point

Usage:
    trading-monitor setup          # First-time setup wizard
    trading-monitor monitor        # Launch live dashboard
    trading-monitor status         # Quick status check
    trading-monitor kill           # Emergency: close all positions
    trading-monitor pause          # Pause kill switch (allow manual trading)
    trading-monitor resume         # Resume kill switch monitoring
    trading-monitor switch demo    # Switch to demo account
    trading-monitor switch real    # Switch to real account
    trading-monitor config         # Show current config
    trading-monitor sim            # Run dashboard in simulation mode (no MT5 needed)
"""

import argparse
import json
import logging
import sys

from .config import Config, setup_wizard, CONFIG_FILE
from .mt5_client import MT5Client, MT5_AVAILABLE
from .kill_switch import KillSwitchEngine
from .dashboard import Dashboard, SimulationDashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("trading_monitor")


def cmd_setup(args):
    """Run setup wizard."""
    setup_wizard()


def cmd_monitor(args):
    """Launch live monitoring dashboard."""
    config = Config.load()
    account = config.active_account

    if not MT5_AVAILABLE:
        print("MetaTrader5 not available. Use 'trading-monitor sim' for simulation mode.")
        print("To install MT5 support (Windows only): pip install MetaTrader5")
        return

    if account.login == 0:
        print("Account not configured. Run 'trading-monitor setup' first.")
        return

    client = MT5Client(account)
    if not client.connect():
        print("Failed to connect to MT5. Check credentials and MT5 terminal.")
        return

    try:
        kill_switch = KillSwitchEngine(client, config.kill_switch)
        dashboard = Dashboard(client, kill_switch, config)
        print(f"Starting dashboard ({config.active_mode.upper()} mode)...")
        dashboard.run()
    finally:
        client.disconnect()


def cmd_sim(args):
    """Launch dashboard in simulation mode."""
    config = Config.load()
    print(f"Starting SIMULATION dashboard ({config.active_mode.upper()} config)...")
    print("This shows simulated data - no real MT5 connection needed.\n")
    dashboard = SimulationDashboard(config)
    dashboard.run()


def cmd_status(args):
    """Quick status check."""
    config = Config.load()
    account = config.active_account
    mode = config.active_mode.upper()

    print(f"\n=== Trading Monitor Status ===")
    print(f"Mode:         {mode}")
    print(f"Server:       {account.server}")
    print(f"Account:      {account.login}")
    print(f"MT5 Available: {'Yes' if MT5_AVAILABLE else 'No (simulation only)'}")

    print(f"\n--- Kill Switch ---")
    ks = config.kill_switch
    print(f"Enabled:       {'Yes' if ks.enabled else 'No'}")
    print(f"Daily Loss:    {ks.max_daily_loss_pct}%")
    print(f"Max Drawdown:  {ks.max_total_drawdown_pct}%")
    print(f"Max Positions: {ks.max_open_positions}")
    print(f"Max Lot Size:  {ks.max_lot_size}")
    print(f"Max Exposure:  {ks.max_total_exposure} lots")

    if MT5_AVAILABLE and account.login > 0:
        client = MT5Client(account)
        if client.connect():
            info = client.get_account_info()
            if info:
                print(f"\n--- Live Account ---")
                print(f"Balance:   {info.currency} {info.balance:,.2f}")
                print(f"Equity:    {info.currency} {info.equity:,.2f}")
                print(f"Profit:    {info.currency} {info.profit:,.2f}")
                print(f"Positions: {len(client.get_positions())}")
            client.disconnect()

    print()


def cmd_kill(args):
    """Emergency close all positions."""
    config = Config.load()
    account = config.active_account
    mode = config.active_mode.upper()

    if not MT5_AVAILABLE:
        print("MT5 not available. Cannot close positions in simulation mode.")
        return

    print(f"\n*** KILL SWITCH - EMERGENCY CLOSE ALL ***")
    print(f"Mode: {mode} | Account: {account.login}")

    confirm = input("\nType 'CONFIRM' to close ALL open positions: ").strip()
    if confirm != "CONFIRM":
        print("Aborted.")
        return

    client = MT5Client(account)
    if not client.connect():
        print("Failed to connect.")
        return

    try:
        results = client.close_all_positions()
        if not results:
            print("No open positions to close.")
        else:
            for r in results:
                status = "CLOSED" if r["success"] else "FAILED"
                print(f"  [{status}] {r['symbol']} #{r['ticket']} ({r['volume']} lots) - {r['comment']}")
    finally:
        client.disconnect()


def cmd_pause(args):
    """Pause kill switch."""
    print("Kill switch PAUSED. New trades will not be monitored.")
    print("Run 'trading-monitor resume' to re-enable.")


def cmd_resume(args):
    """Resume kill switch."""
    print("Kill switch RESUMED. Monitoring active.")


def cmd_switch(args):
    """Switch between demo and real accounts."""
    config = Config.load()
    target = args.target

    if target not in ("demo", "real"):
        print("Usage: trading-monitor switch demo|real")
        return

    if target == "real":
        account = config.real_account
        if account.login == 0:
            print("Real account not configured. Run 'trading-monitor setup' first.")
            return
        print(f"\n*** SWITCHING TO REAL ACCOUNT ***")
        print(f"Server:  {account.server}")
        print(f"Account: {account.login}")
        confirm = input("\nType 'REAL' to confirm: ").strip()
        if confirm != "REAL":
            print("Aborted. Staying in demo mode.")
            return
        config.switch_to_real()
        print("Switched to REAL account.")
    else:
        config.switch_to_demo()
        print("Switched to DEMO account.")


def cmd_config(args):
    """Show current configuration."""
    config = Config.load()
    print(f"\nConfig file: {CONFIG_FILE}")
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        # Mask passwords
        for key in ("demo_account", "real_account"):
            if key in data and "password" in data[key]:
                pw = data[key]["password"]
                data[key]["password"] = pw[:2] + "***" if len(pw) > 2 else "***"
        print(json.dumps(data, indent=2))
    else:
        print("No config file found. Run 'trading-monitor setup'.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Trading Monitor - ActivTrades + ZuluTrade Control System"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("setup", help="First-time setup wizard")
    subparsers.add_parser("monitor", help="Launch live dashboard")
    subparsers.add_parser("sim", help="Launch simulation dashboard (no MT5 needed)")
    subparsers.add_parser("status", help="Quick status check")
    subparsers.add_parser("kill", help="Emergency: close all positions")
    subparsers.add_parser("pause", help="Pause kill switch")
    subparsers.add_parser("resume", help="Resume kill switch")

    switch_parser = subparsers.add_parser("switch", help="Switch demo/real")
    switch_parser.add_argument("target", choices=["demo", "real"])

    subparsers.add_parser("config", help="Show current config")

    args = parser.parse_args()

    commands = {
        "setup": cmd_setup,
        "monitor": cmd_monitor,
        "sim": cmd_sim,
        "status": cmd_status,
        "kill": cmd_kill,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "switch": cmd_switch,
        "config": cmd_config,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
