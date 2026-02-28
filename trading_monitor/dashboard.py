"""
Trading Monitor - Terminal Dashboard
Rich-based terminal UI for monitoring trading account in real-time.
"""

import time
import logging
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from .config import Config
from .mt5_client import MT5Client, AccountInfo, Position
from .kill_switch import KillSwitchEngine, AlertLevel

logger = logging.getLogger("trading_monitor.dashboard")


def _color_pnl(value: float) -> str:
    """Color-code P&L values."""
    if value > 0:
        return f"[bold green]+{value:.2f}[/]"
    elif value < 0:
        return f"[bold red]{value:.2f}[/]"
    return f"[dim]{value:.2f}[/]"


def _color_pct(value: float, invert: bool = False) -> str:
    """Color-code percentage values."""
    good = value <= 0 if not invert else value > 0
    if good:
        return f"[green]{value:.2f}%[/]"
    return f"[red]{value:.2f}%[/]"


def _alert_color(level: AlertLevel) -> str:
    """Get color for alert level."""
    return {
        AlertLevel.INFO: "blue",
        AlertLevel.WARNING: "yellow",
        AlertLevel.CRITICAL: "red",
        AlertLevel.EMERGENCY: "bold white on red",
    }.get(level, "white")


class Dashboard:
    """Real-time terminal dashboard."""

    def __init__(
        self,
        client: MT5Client,
        kill_switch: KillSwitchEngine,
        config: Config,
    ):
        self.client = client
        self.kill_switch = kill_switch
        self.config = config
        self.console = Console()
        self._running = False

    def _build_header(self) -> Panel:
        """Build header panel with account mode and time."""
        mode = self.config.active_mode.upper()
        mode_color = "yellow" if mode == "DEMO" else "red"
        account = self.config.active_account

        header_text = Text()
        header_text.append("TRADING MONITOR", style="bold white")
        header_text.append("  |  ", style="dim")
        header_text.append(f"[{mode}]", style=f"bold {mode_color}")
        header_text.append("  |  ", style="dim")
        header_text.append(f"ActivTrades #{account.login}", style="cyan")
        header_text.append("  |  ", style="dim")
        header_text.append(f"Server: {account.server}", style="dim")
        header_text.append("  |  ", style="dim")
        header_text.append(datetime.now().strftime("%H:%M:%S"), style="white")

        status = "CONNECTED" if self.client.connected else "DISCONNECTED"
        status_color = "green" if self.client.connected else "red"
        header_text.append("  |  ", style="dim")
        header_text.append(status, style=f"bold {status_color}")

        if self.client.is_simulation:
            header_text.append("  |  ", style="dim")
            header_text.append("SIMULATION MODE", style="bold magenta")

        return Panel(Align.center(header_text), style="blue")

    def _build_account_panel(self, info: Optional[AccountInfo]) -> Panel:
        """Build account summary panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="dim", width=16)
        table.add_column("Value", justify="right")

        if info:
            table.add_row("Balance", f"[bold]{info.currency} {info.balance:,.2f}[/]")
            table.add_row("Equity", f"[bold]{info.currency} {info.equity:,.2f}[/]")
            table.add_row("Floating P&L", _color_pnl(info.profit))
            table.add_row("Free Margin", f"{info.currency} {info.free_margin:,.2f}")
            table.add_row("Margin Used", f"{info.currency} {info.margin:,.2f}")
            margin_lvl = f"{info.margin_level:.0f}%" if info.margin_level else "N/A"
            table.add_row("Margin Level", margin_lvl)
            table.add_row("Leverage", f"1:{info.leverage}")

            daily_pnl = self.client.get_daily_pnl()
            table.add_row("", "")
            table.add_row("Daily P&L", _color_pnl(daily_pnl))
        else:
            table.add_row("Status", "[red]No data[/]")

        return Panel(table, title="Account", border_style="cyan")

    def _build_killswitch_panel(self) -> Panel:
        """Build kill switch status panel."""
        status = self.kill_switch.get_status()
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Rule", style="dim", width=18)
        table.add_column("Current", justify="right", width=10)
        table.add_column("Limit", justify="right", width=10)
        table.add_column("Status", justify="center", width=8)

        # Enabled status
        ks_status = "[green]ON[/]" if status["enabled"] else "[red]OFF[/]"
        paused = " [yellow](PAUSED)[/]" if status["paused"] else ""

        # Daily loss
        dl = status["daily_loss_pct"]
        dl_lim = status["daily_loss_limit"]
        dl_ok = "[green]OK[/]" if dl < dl_lim * 0.8 else "[yellow]WARN[/]" if dl < dl_lim else "[red]BREACH[/]"
        table.add_row("Daily Loss", f"{dl:.1f}%", f"{dl_lim:.1f}%", dl_ok)

        # Total drawdown
        dd = status["total_drawdown_pct"]
        dd_lim = status["drawdown_limit"]
        dd_ok = "[green]OK[/]" if dd < dd_lim * 0.7 else "[yellow]WARN[/]" if dd < dd_lim else "[red]BREACH[/]"
        table.add_row("Drawdown", f"{dd:.1f}%", f"{dd_lim:.1f}%", dd_ok)

        # Positions
        pos = status["open_positions"]
        pos_lim = status["max_positions"]
        pos_ok = "[green]OK[/]" if pos < pos_lim * 0.8 else "[yellow]WARN[/]" if pos < pos_lim else "[red]FULL[/]"
        table.add_row("Positions", str(pos), str(pos_lim), pos_ok)

        # Exposure
        exp = status["total_exposure"]
        exp_lim = status["max_exposure"]
        exp_ok = "[green]OK[/]" if exp < exp_lim * 0.8 else "[yellow]WARN[/]" if exp < exp_lim else "[red]HIGH[/]"
        table.add_row("Exposure", f"{exp:.2f}", f"{exp_lim:.1f}", exp_ok)

        title = f"Kill Switch {ks_status}{paused}"
        border = "green" if status["enabled"] and not status["paused"] else "yellow"
        return Panel(table, title=title, border_style=border)

    def _build_positions_panel(self, positions: list[Position]) -> Panel:
        """Build open positions table."""
        table = Table(box=None, padding=(0, 1))
        table.add_column("#", style="dim", width=10)
        table.add_column("Symbol", width=10)
        table.add_column("Type", width=5)
        table.add_column("Lots", justify="right", width=6)
        table.add_column("Open", justify="right", width=10)
        table.add_column("Current", justify="right", width=10)
        table.add_column("P&L", justify="right", width=10)
        table.add_column("SL", justify="right", width=10)
        table.add_column("TP", justify="right", width=10)
        table.add_column("ZT Magic", style="dim", width=8)

        if not positions:
            table.add_row("", "[dim]No open positions[/]", "", "", "", "", "", "", "", "")
        else:
            total_pnl = 0.0
            for p in positions:
                type_color = "green" if p.type == "buy" else "red"
                pnl_str = _color_pnl(p.profit)
                sl_str = f"{p.sl:.5f}" if p.sl > 0 else "[dim]-[/]"
                tp_str = f"{p.tp:.5f}" if p.tp > 0 else "[dim]-[/]"
                magic_str = str(p.magic) if p.magic else "[dim]-[/]"
                table.add_row(
                    str(p.ticket),
                    f"[bold]{p.symbol}[/]",
                    f"[{type_color}]{p.type.upper()}[/]",
                    f"{p.volume:.2f}",
                    f"{p.open_price:.5f}",
                    f"{p.current_price:.5f}",
                    pnl_str,
                    sl_str,
                    tp_str,
                    magic_str,
                )
                total_pnl += p.profit

            table.add_row(
                "", "", "", "", "", "[bold]Total:[/]",
                _color_pnl(total_pnl), "", "", ""
            )

        return Panel(table, title=f"Open Positions ({len(positions)})", border_style="white")

    def _build_alerts_panel(self) -> Panel:
        """Build recent alerts panel."""
        alerts = self.kill_switch.get_recent_alerts(8)
        table = Table(box=None, padding=(0, 1))
        table.add_column("Time", style="dim", width=8)
        table.add_column("Level", width=10)
        table.add_column("Message")
        table.add_column("Action", style="dim")

        if not alerts:
            table.add_row("[dim]-[/]", "[dim]-[/]", "[dim]No alerts[/]", "")
        else:
            for a in reversed(alerts):
                color = _alert_color(a.level)
                table.add_row(
                    a.timestamp.strftime("%H:%M:%S"),
                    f"[{color}]{a.level.value.upper()}[/]",
                    a.message,
                    a.action_taken or "-",
                )

        return Panel(table, title="Alerts", border_style="yellow")

    def _build_help_panel(self) -> Panel:
        """Build help/commands panel."""
        help_text = (
            "[dim]Commands: "
            "[bold]Ctrl+C[/] quit  |  "
            "[bold]trading-monitor kill[/] close all  |  "
            "[bold]trading-monitor pause[/] pause  |  "
            "[bold]trading-monitor resume[/] resume  |  "
            "[bold]trading-monitor switch demo|real[/] switch mode"
            "[/]"
        )
        return Panel(help_text, style="dim")

    def build_layout(self) -> Layout:
        """Build the full dashboard layout."""
        layout = Layout()

        # Get live data
        info = self.client.get_account_info() if self.client.connected else None
        positions = self.client.get_positions() if self.client.connected else []

        # Run kill switch checks
        if self.client.connected:
            self.kill_switch.check()

        layout.split_column(
            Layout(self._build_header(), size=3),
            Layout(name="top", size=12),
            Layout(self._build_positions_panel(positions), name="positions"),
            Layout(self._build_alerts_panel(), size=12),
            Layout(self._build_help_panel(), size=3),
        )

        layout["top"].split_row(
            Layout(self._build_account_panel(info)),
            Layout(self._build_killswitch_panel()),
        )

        return layout

    def render_once(self):
        """Render dashboard once (for non-live mode)."""
        self.console.clear()
        self.console.print(self.build_layout())

    def run(self):
        """Run live dashboard with auto-refresh."""
        self._running = True
        interval = self.config.dashboard.refresh_interval_sec

        try:
            with Live(
                self.build_layout(),
                console=self.console,
                refresh_per_second=1,
                screen=True,
            ) as live:
                while self._running:
                    time.sleep(interval)
                    live.update(self.build_layout())
        except KeyboardInterrupt:
            self._running = False
            self.console.print("\n[yellow]Dashboard stopped.[/]")

    def stop(self):
        """Stop the dashboard."""
        self._running = False


class SimulationDashboard(Dashboard):
    """Dashboard with simulated data for testing without MT5."""

    def __init__(self, config: Config):
        # Create a dummy client
        client = MT5Client(config.active_account)
        ks_config = config.kill_switch
        kill_switch = KillSwitchEngine(client, ks_config)
        super().__init__(client, kill_switch, config)
        self._sim_data = self._generate_sim_data()

    def _generate_sim_data(self) -> dict:
        """Generate simulated data matching ActivTrades #958831."""
        return {
            "info": AccountInfo(
                login=958831,
                server="ActivTrades-Server",
                balance=657.68,
                equity=661.42,
                margin=12.50,
                free_margin=648.92,
                margin_level=5291.36,
                profit=3.74,
                currency="EUR",
                leverage=400,
                name="CARMARGO PASSINATO",
                company="ActivTrades Plc",
            ),
            "positions": [
                Position(
                    ticket=200001, symbol="EURUSD", type="buy",
                    volume=0.02, open_price=1.08450, current_price=1.08520,
                    profit=1.40, swap=-0.10, commission=-0.14,
                    open_time=datetime.now(), sl=1.08200, tp=1.08800,
                    magic=10001, comment="ZuluTrade"
                ),
                Position(
                    ticket=200002, symbol="XAUUSD", type="buy",
                    volume=0.01, open_price=2650.50, current_price=2655.80,
                    profit=2.34, swap=-0.30, commission=-0.10,
                    open_time=datetime.now(), sl=2640.00, tp=2670.00,
                    magic=10002, comment="ZuluTrade"
                ),
            ],
        }

    def _build_account_panel(self, info: Optional[AccountInfo]) -> Panel:
        return super()._build_account_panel(self._sim_data["info"])

    def _build_positions_panel(self, positions: list[Position]) -> Panel:
        return super()._build_positions_panel(self._sim_data["positions"])

    def build_layout(self) -> Layout:
        """Build layout with simulated data."""
        layout = Layout()

        info = self._sim_data["info"]
        positions = self._sim_data["positions"]

        layout.split_column(
            Layout(self._build_header(), size=3),
            Layout(name="top", size=12),
            Layout(self._build_positions_panel(positions), name="positions"),
            Layout(self._build_alerts_panel(), size=12),
            Layout(self._build_help_panel(), size=3),
        )

        layout["top"].split_row(
            Layout(self._build_account_panel(info)),
            Layout(self._build_killswitch_panel()),
        )

        return layout
