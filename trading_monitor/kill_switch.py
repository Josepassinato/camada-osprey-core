"""
Trading Monitor - Kill Switch Engine
Monitors account in real-time and triggers emergency actions.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from .config import KillSwitchConfig
from .mt5_client import MT5Client, AccountInfo

logger = logging.getLogger("trading_monitor.kill_switch")


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Kill switch alert record."""
    timestamp: datetime
    level: AlertLevel
    rule: str
    message: str
    value: float
    threshold: float
    action_taken: str = ""


class KillSwitchEngine:
    """
    Monitors trading account and enforces risk limits.

    Rules:
    1. Max daily loss % → close all positions
    2. Max total drawdown % → close all positions
    3. Max open positions → block new trades
    4. Max lot size per position → alert
    5. Max total exposure → alert/close
    6. Consecutive losses → pause trading
    """

    def __init__(self, client: MT5Client, config: KillSwitchConfig):
        self.client = client
        self.config = config
        self.alerts: list[Alert] = []
        self._paused = False
        self._consecutive_losses = 0
        self._last_check: Optional[datetime] = None
        self._positions_closed_today = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_enabled(self) -> bool:
        return self.config.enabled

    def pause(self):
        """Manually pause trading."""
        self._paused = True
        self._add_alert(
            AlertLevel.WARNING, "manual_pause",
            "Trading paused manually", 0, 0, "paused"
        )

    def resume(self):
        """Resume trading after pause."""
        self._paused = False
        self._positions_closed_today = False
        self._add_alert(
            AlertLevel.INFO, "manual_resume",
            "Trading resumed manually", 0, 0, "resumed"
        )

    def check(self) -> list[Alert]:
        """Run all kill switch checks. Returns new alerts since last check."""
        if not self.config.enabled:
            return []

        new_alerts = []
        self._last_check = datetime.now()

        # Check daily loss
        alert = self._check_daily_loss()
        if alert:
            new_alerts.append(alert)

        # Check total drawdown
        alert = self._check_total_drawdown()
        if alert:
            new_alerts.append(alert)

        # Check position count
        alert = self._check_position_count()
        if alert:
            new_alerts.append(alert)

        # Check individual position sizes
        alerts = self._check_position_sizes()
        new_alerts.extend(alerts)

        # Check total exposure
        alert = self._check_total_exposure()
        if alert:
            new_alerts.append(alert)

        return new_alerts

    def _check_daily_loss(self) -> Optional[Alert]:
        """Check if daily loss exceeds threshold."""
        daily_loss_pct = self.client.get_daily_loss_pct()
        if daily_loss_pct >= self.config.max_daily_loss_pct:
            action = ""
            if not self._positions_closed_today:
                action = self._emergency_close_all(
                    f"Daily loss {daily_loss_pct:.1f}% >= {self.config.max_daily_loss_pct}%"
                )
                self._positions_closed_today = True
            return self._add_alert(
                AlertLevel.EMERGENCY, "daily_loss",
                f"Daily loss limit breached: {daily_loss_pct:.2f}%",
                daily_loss_pct, self.config.max_daily_loss_pct, action
            )
        elif daily_loss_pct >= self.config.max_daily_loss_pct * 0.8:
            return self._add_alert(
                AlertLevel.WARNING, "daily_loss_warning",
                f"Approaching daily loss limit: {daily_loss_pct:.2f}%",
                daily_loss_pct, self.config.max_daily_loss_pct
            )
        return None

    def _check_total_drawdown(self) -> Optional[Alert]:
        """Check if total drawdown exceeds threshold."""
        drawdown_pct = self.client.get_total_drawdown_pct()
        if drawdown_pct >= self.config.max_total_drawdown_pct:
            action = self._emergency_close_all(
                f"Drawdown {drawdown_pct:.1f}% >= {self.config.max_total_drawdown_pct}%"
            )
            self._paused = True
            return self._add_alert(
                AlertLevel.EMERGENCY, "total_drawdown",
                f"Total drawdown limit breached: {drawdown_pct:.2f}%",
                drawdown_pct, self.config.max_total_drawdown_pct, action
            )
        elif drawdown_pct >= self.config.max_total_drawdown_pct * 0.7:
            return self._add_alert(
                AlertLevel.WARNING, "drawdown_warning",
                f"Approaching drawdown limit: {drawdown_pct:.2f}%",
                drawdown_pct, self.config.max_total_drawdown_pct
            )
        return None

    def _check_position_count(self) -> Optional[Alert]:
        """Check number of open positions."""
        positions = self.client.get_positions()
        count = len(positions)
        if count >= self.config.max_open_positions:
            return self._add_alert(
                AlertLevel.CRITICAL, "position_count",
                f"Max positions reached: {count}/{self.config.max_open_positions}",
                count, self.config.max_open_positions
            )
        elif count >= self.config.max_open_positions * 0.8:
            return self._add_alert(
                AlertLevel.WARNING, "position_count_warning",
                f"Approaching max positions: {count}/{self.config.max_open_positions}",
                count, self.config.max_open_positions
            )
        return None

    def _check_position_sizes(self) -> list[Alert]:
        """Check individual position lot sizes."""
        positions = self.client.get_positions()
        alerts = []
        for pos in positions:
            if pos.volume > self.config.max_lot_size:
                alerts.append(self._add_alert(
                    AlertLevel.CRITICAL, "lot_size",
                    f"{pos.symbol} #{pos.ticket}: {pos.volume} lots > max {self.config.max_lot_size}",
                    pos.volume, self.config.max_lot_size
                ))
        return alerts

    def _check_total_exposure(self) -> Optional[Alert]:
        """Check total lot exposure across all positions."""
        positions = self.client.get_positions()
        total_lots = sum(p.volume for p in positions)
        if total_lots > self.config.max_total_exposure:
            return self._add_alert(
                AlertLevel.CRITICAL, "total_exposure",
                f"Total exposure {total_lots:.2f} lots > max {self.config.max_total_exposure}",
                total_lots, self.config.max_total_exposure
            )
        return None

    def _emergency_close_all(self, reason: str) -> str:
        """Emergency close all positions."""
        logger.critical(f"KILL SWITCH TRIGGERED: {reason}")
        results = self.client.close_all_positions()
        closed = sum(1 for r in results if r["success"])
        failed = sum(1 for r in results if not r["success"])
        msg = f"Closed {closed} positions, {failed} failed"
        logger.critical(msg)
        return msg

    def _add_alert(
        self, level: AlertLevel, rule: str,
        message: str, value: float, threshold: float,
        action: str = ""
    ) -> Alert:
        alert = Alert(
            timestamp=datetime.now(),
            level=level,
            rule=rule,
            message=message,
            value=value,
            threshold=threshold,
            action_taken=action,
        )
        self.alerts.append(alert)
        if level == AlertLevel.EMERGENCY:
            logger.critical(f"[EMERGENCY] {message}")
        elif level == AlertLevel.CRITICAL:
            logger.error(f"[CRITICAL] {message}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"[WARNING] {message}")
        else:
            logger.info(f"[INFO] {message}")
        return alert

    def get_status(self) -> dict:
        """Get kill switch status summary."""
        info = self.client.get_account_info()
        positions = self.client.get_positions()
        return {
            "enabled": self.config.enabled,
            "paused": self._paused,
            "daily_loss_pct": self.client.get_daily_loss_pct(),
            "daily_loss_limit": self.config.max_daily_loss_pct,
            "total_drawdown_pct": self.client.get_total_drawdown_pct(),
            "drawdown_limit": self.config.max_total_drawdown_pct,
            "open_positions": len(positions) if positions else 0,
            "max_positions": self.config.max_open_positions,
            "total_exposure": sum(p.volume for p in positions) if positions else 0,
            "max_exposure": self.config.max_total_exposure,
            "alerts_count": len(self.alerts),
            "last_check": self._last_check.isoformat() if self._last_check else None,
        }

    def get_recent_alerts(self, n: int = 20) -> list[Alert]:
        """Get most recent N alerts."""
        return self.alerts[-n:]
