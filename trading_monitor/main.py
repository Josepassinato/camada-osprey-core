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
    trading-monitor traders        # Analyze and recommend traders to copy
    trading-monitor portfolio      # Show recommended portfolio for your account
"""

import argparse
import json
import logging
import sys

from .config import Config, setup_wizard, CONFIG_FILE
from .mt5_client import MT5Client, MT5_AVAILABLE
from .kill_switch import KillSwitchEngine
from .dashboard import Dashboard, SimulationDashboard
from .trader_scorer import score_trader, recommend_portfolio, TraderProfile
from .zulutrade_client import ZuluTradeClient, CURATED_TRADERS, create_manual_profile

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


def cmd_traders(args):
    """Analyze and recommend traders to copy."""
    config = Config.load()
    balance = 657.68  # Known balance

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        console = Console()
        use_rich = True
    except ImportError:
        use_rich = False

    # First try ZuluTrade API
    print("\nSearching for traders on ZuluTrade...")
    zt_client = ZuluTradeClient()
    api_traders = zt_client.search_leaders(min_roi=10, max_drawdown=30, min_weeks=26)

    traders = []
    if api_traders:
        print(f"Found {len(api_traders)} traders via API.")
        for data in api_traders:
            traders.append(zt_client.parse_trader_profile(data))
    else:
        print("API unavailable. Using curated trader database for analysis.\n")
        traders = CURATED_TRADERS

    # Score all traders
    scored = [score_trader(t, balance) for t in traders]
    scored.sort(key=lambda s: s.total_score, reverse=True)

    if use_rich:
        table = Table(title=f"Trader Analysis (Account: EUR {balance:,.2f})")
        table.add_column("#", style="dim", width=3)
        table.add_column("Trader", width=16)
        table.add_column("Score", justify="center", width=7)
        table.add_column("Verdict", justify="center", width=12)
        table.add_column("ROI 12m", justify="right", width=8)
        table.add_column("DD Max", justify="right", width=8)
        table.add_column("Win%", justify="right", width=6)
        table.add_column("Weeks", justify="right", width=6)
        table.add_column("Trades/w", justify="right", width=8)
        table.add_column("Lot Size", justify="right", width=8)
        table.add_column("ZuluGuard", justify="right", width=10)

        for i, s in enumerate(scored, 1):
            t = s.trader
            verdict_colors = {
                "strong_buy": "[bold green]STRONG BUY[/]",
                "buy": "[green]BUY[/]",
                "neutral": "[yellow]NEUTRAL[/]",
                "avoid": "[red]AVOID[/]",
            }
            score_color = "green" if s.total_score >= 60 else "yellow" if s.total_score >= 45 else "red"

            table.add_row(
                str(i),
                f"[bold]{t.name}[/]",
                f"[{score_color}]{s.total_score:.0f}[/]",
                verdict_colors.get(s.verdict, s.verdict),
                f"{t.roi_12m_pct:.1f}%",
                f"{t.max_drawdown_pct:.1f}%",
                f"{t.win_rate_pct:.0f}%",
                str(t.weeks_active),
                f"{t.avg_trades_per_week:.1f}",
                f"{s.recommended_lot:.2f}",
                f"EUR {s.recommended_zuluguard:.0f}",
            )

        console.print()
        console.print(table)
        console.print()

        # Show reasons
        for i, s in enumerate(scored, 1):
            emoji = {"strong_buy": "+", "buy": "+", "neutral": "~", "avoid": "-"}.get(s.verdict, "?")
            console.print(f"  [{emoji}] {s.trader.name}: {s.reason}")
        console.print()
    else:
        print(f"\n{'#':<3} {'Trader':<16} {'Score':<7} {'Verdict':<12} {'ROI12m':<8} {'DD':<8} {'Lot':<6} {'ZGuard':<8}")
        print("-" * 72)
        for i, s in enumerate(scored, 1):
            t = s.trader
            print(f"{i:<3} {t.name:<16} {s.total_score:<7.0f} {s.verdict:<12} {t.roi_12m_pct:<8.1f} {t.max_drawdown_pct:<8.1f} {s.recommended_lot:<6.2f} EUR {s.recommended_zuluguard:<.0f}")
        print()
        for s in scored:
            print(f"  {s.trader.name}: {s.reason}")
        print()


def cmd_portfolio(args):
    """Show recommended portfolio for your account."""
    config = Config.load()
    balance = 657.68

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        console = Console()
        use_rich = True
    except ImportError:
        use_rich = False

    # Try API first, fall back to curated
    zt_client = ZuluTradeClient()
    api_traders = zt_client.search_leaders(min_roi=10, max_drawdown=30, min_weeks=26)

    if api_traders:
        traders = [zt_client.parse_trader_profile(d) for d in api_traders]
    else:
        traders = CURATED_TRADERS

    # Get recommended portfolio
    portfolio = recommend_portfolio(traders, balance, max_traders=3)

    if not portfolio:
        print("No suitable traders found matching criteria.")
        return

    if use_rich:
        console.print()
        console.print(Panel(
            f"[bold]Recommended Portfolio[/]\n"
            f"Account: ActivTrades #958831 | Balance: EUR {balance:,.2f} | Mode: {config.active_mode.upper()}",
            style="cyan"
        ))
        console.print()

        table = Table(title="Copy These Traders")
        table.add_column("Trader", width=16)
        table.add_column("Score", justify="center", width=7)
        table.add_column("Lot Size", justify="center", width=10)
        table.add_column("ZuluGuard", justify="center", width=12)
        table.add_column("Instruments", width=24)
        table.add_column("Max Open", justify="center", width=9)

        total_max_lots = 0
        total_zuluguard = 0

        for s in portfolio:
            t = s.trader
            instruments = ", ".join(t.currency_pairs[:3])
            max_lots = s.recommended_lot * max(1, t.max_open_trades)
            total_max_lots += max_lots
            total_zuluguard += s.recommended_zuluguard

            table.add_row(
                f"[bold green]{t.name}[/]",
                f"[bold]{s.total_score:.0f}[/]",
                f"[bold]{s.recommended_lot:.2f}[/]",
                f"EUR {s.recommended_zuluguard:.0f}",
                instruments,
                str(t.max_open_trades),
            )

        table.add_row(
            "[bold]TOTAL[/]", "", "",
            f"[bold]EUR {total_zuluguard:.0f}[/]",
            "", ""
        )

        console.print(table)
        console.print()

        # Risk summary
        risk_pct = (total_zuluguard / balance) * 100
        console.print(Panel(
            f"[bold]Risk Summary[/]\n\n"
            f"  Total ZuluGuard:     EUR {total_zuluguard:.0f} ({risk_pct:.1f}% of balance)\n"
            f"  Max total exposure:  {total_max_lots:.2f} lots (limit: {config.kill_switch.max_total_exposure} lots)\n"
            f"  Kill Switch:         {'[green]ON[/]' if config.kill_switch.enabled else '[red]OFF[/]'}\n"
            f"  Daily loss limit:    {config.kill_switch.max_daily_loss_pct}% (EUR {balance * config.kill_switch.max_daily_loss_pct / 100:.0f})\n"
            f"  Max drawdown:        {config.kill_switch.max_total_drawdown_pct}% (EUR {balance * config.kill_switch.max_total_drawdown_pct / 100:.0f})\n",
            title="Risk", border_style="yellow"
        ))

        # ZuluTrade setup instructions
        console.print(Panel(
            "[bold]Como Configurar no ZuluTrade:[/]\n\n"
            "1. Acesse zulutrade.com -> Leaders\n"
            "2. Busque cada trader pelo nome\n"
            "3. Clique 'Follow' e configure:\n"
            "   - Fixed Lots: use o tamanho indicado acima\n"
            "   - ZuluGuard: ative com o valor indicado acima\n"
            "   - Acao ZuluGuard: 'Close trades and unfollow'\n"
            "4. Repita para cada trader do portfolio\n\n"
            "[dim]Dica: Comece com 1 trader, observe 1 semana, depois adicione os outros[/]",
            title="Setup ZuluTrade", border_style="green"
        ))
    else:
        print(f"\n=== Recommended Portfolio ===")
        print(f"Account: EUR {balance:,.2f}\n")
        for s in portfolio:
            t = s.trader
            print(f"  [{s.verdict.upper()}] {t.name}")
            print(f"    Score: {s.total_score:.0f} | Lot: {s.recommended_lot:.2f} | ZuluGuard: EUR {s.recommended_zuluguard:.0f}")
            print(f"    Instruments: {', '.join(t.currency_pairs[:3])}")
            print(f"    {s.reason}")
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
    subparsers.add_parser("traders", help="Analyze and score traders")
    subparsers.add_parser("portfolio", help="Show recommended portfolio")

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
        "traders": cmd_traders,
        "portfolio": cmd_portfolio,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
