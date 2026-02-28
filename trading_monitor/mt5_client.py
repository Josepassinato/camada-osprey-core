"""
Trading Monitor - MT5 Client
Connection layer for ActivTrades via MetaTrader 5.
Falls back to simulation mode when MT5 is unavailable (Linux/macOS).
"""

import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .config import AccountConfig

logger = logging.getLogger("trading_monitor.mt5")

# Try to import MetaTrader5 (Windows only)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None


@dataclass
class Position:
    """Open position data."""
    ticket: int
    symbol: str
    type: str          # "buy" or "sell"
    volume: float
    open_price: float
    current_price: float
    profit: float
    swap: float
    commission: float
    open_time: datetime
    sl: float = 0.0
    tp: float = 0.0
    magic: int = 0     # ZuluTrade uses magic numbers to identify traders
    comment: str = ""


@dataclass
class AccountInfo:
    """Account summary."""
    login: int = 0
    server: str = ""
    balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    free_margin: float = 0.0
    margin_level: float = 0.0
    profit: float = 0.0
    currency: str = "USD"
    leverage: int = 0
    name: str = ""
    company: str = ""


@dataclass
class DealRecord:
    """Closed trade record."""
    ticket: int
    symbol: str
    type: str
    volume: float
    open_price: float
    close_price: float
    profit: float
    swap: float
    commission: float
    open_time: datetime
    close_time: datetime
    magic: int = 0
    comment: str = ""


class MT5Client:
    """MetaTrader 5 connection client for ActivTrades."""

    def __init__(self, account_config: AccountConfig):
        self.account_config = account_config
        self._connected = False
        self._initial_balance: Optional[float] = None
        self._day_start_balance: Optional[float] = None
        self._day_start_date: Optional[str] = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def is_simulation(self) -> bool:
        return not MT5_AVAILABLE

    def connect(self) -> bool:
        """Connect to MT5 terminal."""
        if not MT5_AVAILABLE:
            logger.warning(
                "MetaTrader5 package not available. "
                "Install on Windows: pip install MetaTrader5. "
                "Running in simulation mode."
            )
            self._connected = False
            return False

        if not mt5.initialize():
            logger.error(f"MT5 initialize() failed: {mt5.last_error()}")
            return False

        authorized = mt5.login(
            login=self.account_config.login,
            password=self.account_config.password,
            server=self.account_config.server,
        )
        if not authorized:
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False

        self._connected = True
        info = self.get_account_info()
        if info:
            self._initial_balance = info.balance
            self._day_start_balance = info.balance
            self._day_start_date = datetime.now().strftime("%Y-%m-%d")
        logger.info(
            f"Connected to {self.account_config.server} "
            f"(account {self.account_config.login}, "
            f"mode: {self.account_config.label})"
        )
        return True

    def disconnect(self):
        """Disconnect from MT5."""
        if MT5_AVAILABLE and self._connected:
            mt5.shutdown()
        self._connected = False

    def get_account_info(self) -> Optional[AccountInfo]:
        """Get current account info."""
        if not self._connected:
            return None
        info = mt5.account_info()
        if info is None:
            return None
        return AccountInfo(
            login=info.login,
            server=info.server,
            balance=info.balance,
            equity=info.equity,
            margin=info.margin,
            free_margin=info.margin_free,
            margin_level=info.margin_level if info.margin_level else 0.0,
            profit=info.profit,
            currency=info.currency,
            leverage=info.leverage,
            name=info.name,
            company=info.company,
        )

    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        if not self._connected:
            return []
        positions = mt5.positions_get()
        if positions is None:
            return []
        result = []
        for p in positions:
            pos_type = "buy" if p.type == mt5.ORDER_TYPE_BUY else "sell"
            result.append(Position(
                ticket=p.ticket,
                symbol=p.symbol,
                type=pos_type,
                volume=p.volume,
                open_price=p.price_open,
                current_price=p.price_current,
                profit=p.profit,
                swap=p.swap,
                commission=p.commission if hasattr(p, 'commission') else 0.0,
                open_time=datetime.fromtimestamp(p.time, tz=timezone.utc),
                sl=p.sl,
                tp=p.tp,
                magic=p.magic,
                comment=p.comment,
            ))
        return result

    def get_daily_deals(self) -> list[DealRecord]:
        """Get today's closed trades."""
        if not self._connected:
            return []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        now = datetime.now()
        deals = mt5.history_deals_get(today, now)
        if deals is None:
            return []
        result = []
        for d in deals:
            if d.entry == mt5.DEAL_ENTRY_OUT:  # closing deals only
                deal_type = "buy" if d.type == mt5.DEAL_TYPE_BUY else "sell"
                result.append(DealRecord(
                    ticket=d.ticket,
                    symbol=d.symbol,
                    type=deal_type,
                    volume=d.volume,
                    open_price=d.price,
                    close_price=d.price,
                    profit=d.profit,
                    swap=d.swap,
                    commission=d.commission,
                    open_time=datetime.fromtimestamp(d.time, tz=timezone.utc),
                    close_time=datetime.fromtimestamp(d.time, tz=timezone.utc),
                    magic=d.magic,
                    comment=d.comment,
                ))
        return result

    def close_all_positions(self) -> list[dict]:
        """Emergency: close all open positions."""
        if not self._connected:
            return []
        positions = mt5.positions_get()
        if not positions:
            return []
        results = []
        for pos in positions:
            close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            symbol_info = mt5.symbol_info(pos.symbol)
            if symbol_info is None:
                continue
            price = symbol_info.bid if pos.type == mt5.ORDER_TYPE_BUY else symbol_info.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": pos.ticket,
                "price": price,
                "deviation": 20,
                "magic": 999999,
                "comment": "kill_switch_close",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            results.append({
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "success": result.retcode == mt5.TRADE_RETCODE_DONE if result else False,
                "comment": result.comment if result else "failed",
            })
        return results

    def get_daily_pnl(self) -> float:
        """Calculate today's P&L."""
        info = self.get_account_info()
        if not info:
            return 0.0
        today = datetime.now().strftime("%Y-%m-%d")
        if self._day_start_date != today:
            self._day_start_balance = info.balance
            self._day_start_date = today
        return info.equity - (self._day_start_balance or info.balance)

    def get_total_drawdown_pct(self) -> float:
        """Calculate drawdown from initial balance."""
        info = self.get_account_info()
        if not info or not self._initial_balance:
            return 0.0
        if self._initial_balance == 0:
            return 0.0
        return ((self._initial_balance - info.equity) / self._initial_balance) * 100

    def get_daily_loss_pct(self) -> float:
        """Calculate today's loss as % of balance."""
        info = self.get_account_info()
        if not info or not self._day_start_balance:
            return 0.0
        if self._day_start_balance == 0:
            return 0.0
        daily_pnl = info.equity - self._day_start_balance
        if daily_pnl >= 0:
            return 0.0
        return (abs(daily_pnl) / self._day_start_balance) * 100
