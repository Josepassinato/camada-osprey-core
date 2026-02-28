"""
Trading Monitor - Trader Scoring & Recommendation Engine
Analyzes ZuluTrade traders and recommends the best for copy trading.
Calibrated for small accounts (~660 EUR).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TraderProfile:
    """ZuluTrade trader profile data."""
    name: str
    provider_id: str
    roi_pct: float               # Total ROI %
    roi_12m_pct: float           # Last 12 months ROI %
    max_drawdown_pct: float      # Maximum drawdown %
    weeks_active: int            # Weeks trading on ZuluTrade
    followers: int               # Number of followers
    avg_trades_per_week: float   # Average trades/week
    win_rate_pct: float          # Win rate %
    avg_pips_per_trade: float    # Average pips per trade
    max_open_trades: int         # Max simultaneous trades
    currency_pairs: list[str]    # Instruments traded
    nme: float = 0.0             # Normalized Median Expectancy
    sharpe_ratio: float = 0.0    # Risk-adjusted return
    slippage_avg: float = 0.0    # Average slippage in pips
    zulurank: int = 0            # ZuluTrade ranking


@dataclass
class TraderScore:
    """Scored trader with recommendation."""
    trader: TraderProfile
    total_score: float           # 0-100
    risk_score: float            # 0-100 (higher = safer)
    consistency_score: float     # 0-100
    recommended_lot: float       # Lot size for your account
    recommended_zuluguard: float  # ZuluGuard amount in EUR
    reason: str                  # Why recommended/rejected
    verdict: str                 # "strong_buy", "buy", "neutral", "avoid"


# Scoring weights
WEIGHTS = {
    "roi_12m": 0.15,
    "drawdown": 0.20,
    "win_rate": 0.20,
    "experience": 0.10,
    "followers": 0.05,
    "trade_frequency": 0.10,
    "risk_management": 0.20,
}


def score_trader(trader: TraderProfile, account_balance: float = 657.68) -> TraderScore:
    """
    Score a trader on a 0-100 scale.
    Higher = better for copy trading with small account.
    """
    scores = {}

    # 1. ROI (12 months) - sweet spot 15-80%, penalize extremes
    roi = trader.roi_12m_pct
    if roi <= 0:
        scores["roi_12m"] = 0
    elif roi <= 15:
        scores["roi_12m"] = roi * 3  # 0-45
    elif roi <= 50:
        scores["roi_12m"] = 45 + (roi - 15) * 1.57  # 45-100
    elif roi <= 100:
        scores["roi_12m"] = 100 - (roi - 50) * 0.5  # 100-75 (slight penalty for too high)
    else:
        scores["roi_12m"] = max(50, 100 - roi * 0.3)  # High ROI = likely high risk

    # 2. Max Drawdown - lower is better, critical for small accounts
    dd = trader.max_drawdown_pct
    if dd <= 10:
        scores["drawdown"] = 100
    elif dd <= 20:
        scores["drawdown"] = 100 - (dd - 10) * 3  # 100-70
    elif dd <= 35:
        scores["drawdown"] = 70 - (dd - 20) * 2.67  # 70-30
    elif dd <= 50:
        scores["drawdown"] = 30 - (dd - 35) * 2  # 30-0
    else:
        scores["drawdown"] = 0

    # 3. Win rate
    wr = trader.win_rate_pct
    if wr >= 70:
        scores["win_rate"] = min(100, 60 + (wr - 70) * 1.33)
    elif wr >= 55:
        scores["win_rate"] = 30 + (wr - 55) * 2
    else:
        scores["win_rate"] = max(0, wr * 0.55)

    # 4. Experience (weeks active)
    weeks = trader.weeks_active
    if weeks >= 52:  # 1+ year
        scores["experience"] = min(100, 60 + (weeks - 52) * 0.38)
    elif weeks >= 26:  # 6+ months
        scores["experience"] = 30 + (weeks - 26) * 1.15
    elif weeks >= 12:
        scores["experience"] = weeks * 2.5
    else:
        scores["experience"] = max(0, weeks * 1.5)  # Penalize new traders

    # 5. Followers (social validation)
    f = trader.followers
    if f >= 200:
        scores["followers"] = 100
    elif f >= 50:
        scores["followers"] = 50 + (f - 50) * 0.33
    elif f >= 10:
        scores["followers"] = f
    else:
        scores["followers"] = max(0, f * 3)

    # 6. Trade frequency - avoid overtraders and undertraders
    freq = trader.avg_trades_per_week
    if 2 <= freq <= 8:
        scores["trade_frequency"] = 100
    elif 1 <= freq < 2:
        scores["trade_frequency"] = 60
    elif 8 < freq <= 15:
        scores["trade_frequency"] = 80 - (freq - 8) * 5
    elif freq > 15:
        scores["trade_frequency"] = max(0, 45 - (freq - 15) * 3)  # Overtrading penalty
    else:
        scores["trade_frequency"] = 30  # Very low frequency

    # 7. Risk management (max open trades + drawdown combo)
    mot = trader.max_open_trades
    if mot <= 3:
        rm_score = 100
    elif mot <= 5:
        rm_score = 80
    elif mot <= 8:
        rm_score = 60
    elif mot <= 12:
        rm_score = 40
    else:
        rm_score = max(0, 40 - (mot - 12) * 5)

    # Bonus if drawdown is low relative to ROI
    if trader.roi_12m_pct > 0 and trader.max_drawdown_pct > 0:
        risk_reward = trader.roi_12m_pct / trader.max_drawdown_pct
        if risk_reward >= 2:
            rm_score = min(100, rm_score + 20)
        elif risk_reward >= 1:
            rm_score = min(100, rm_score + 10)
    scores["risk_management"] = rm_score

    # Calculate weighted total
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    risk_score = (scores["drawdown"] + scores["risk_management"]) / 2
    consistency_score = scores["win_rate"]

    # Calculate recommended lot size for this account
    recommended_lot = _calc_lot_size(trader, account_balance)

    # Calculate ZuluGuard
    max_loss_per_trader = account_balance * 0.075  # 7.5% of account per trader
    recommended_zuluguard = round(max_loss_per_trader, 2)

    # Verdict
    if total >= 75 and risk_score >= 60:
        verdict = "strong_buy"
        reason = f"Score {total:.0f}/100. Low risk, consistent returns."
    elif total >= 60 and risk_score >= 45:
        verdict = "buy"
        reason = f"Score {total:.0f}/100. Good balance of risk/reward."
    elif total >= 45:
        verdict = "neutral"
        reason = f"Score {total:.0f}/100. Acceptable but has weaknesses."
    else:
        verdict = "avoid"
        reasons = []
        if scores["drawdown"] < 40:
            reasons.append(f"high drawdown ({trader.max_drawdown_pct:.0f}%)")
        if scores["roi_12m"] < 30:
            reasons.append(f"low ROI ({trader.roi_12m_pct:.1f}%)")
        if scores["experience"] < 30:
            reasons.append(f"insufficient track record ({trader.weeks_active}w)")
        if scores["trade_frequency"] < 40:
            reasons.append("bad trade frequency")
        reason = f"Score {total:.0f}/100. Avoid: " + ", ".join(reasons) if reasons else f"Score {total:.0f}/100. Below threshold."

    return TraderScore(
        trader=trader,
        total_score=round(total, 1),
        risk_score=round(risk_score, 1),
        consistency_score=round(consistency_score, 1),
        recommended_lot=recommended_lot,
        recommended_zuluguard=recommended_zuluguard,
        reason=reason,
        verdict=verdict,
    )


def _calc_lot_size(trader: TraderProfile, balance: float) -> float:
    """
    Calculate safe lot size for copy trading.
    Rule: risk max 1-2% of account per trade, considering trader's max open trades.
    """
    # Max risk per signal: 1.5% of balance
    risk_per_trade_eur = balance * 0.015

    # Assume ~100 pips SL average, ~10 EUR/pip for 0.01 lot on majors
    # 0.01 lot EURUSD: 1 pip = ~$0.10 = ~0.09 EUR
    eur_per_pip_per_microlot = 0.09

    # Target: risk_per_trade = lot_size * avg_sl_pips * eur_per_pip
    avg_sl_pips = 50  # Conservative estimate
    max_lot_from_risk = risk_per_trade_eur / (avg_sl_pips * eur_per_pip_per_microlot * 100)

    # Also limit by max open trades of the trader
    max_concurrent = max(1, trader.max_open_trades)
    total_risk_limit = balance * 0.05  # Max 5% total risk at once
    max_lot_from_concurrent = total_risk_limit / (max_concurrent * avg_sl_pips * eur_per_pip_per_microlot * 100)

    # Take the smaller
    lot = min(max_lot_from_risk, max_lot_from_concurrent)

    # Round down to nearest 0.01
    lot = max(0.01, round(lot - 0.005, 2))

    # Hard cap
    return min(lot, 0.05)


def recommend_portfolio(
    traders: list[TraderProfile],
    account_balance: float = 657.68,
    max_traders: int = 3,
) -> list[TraderScore]:
    """
    Recommend a portfolio of traders to copy.
    For a 657 EUR account, max 3 traders to maintain diversification
    without over-distributing small capital.
    """
    scored = [score_trader(t, account_balance) for t in traders]

    # Filter: only strong_buy and buy
    viable = [s for s in scored if s.verdict in ("strong_buy", "buy")]

    # Sort by total score descending
    viable.sort(key=lambda s: s.total_score, reverse=True)

    # Ensure diversity: don't pick traders with same style/instruments
    selected = []
    for s in viable:
        if len(selected) >= max_traders:
            break

        # Check overlap with already selected
        overlap = False
        for existing in selected:
            # If >60% instrument overlap, skip
            existing_pairs = set(existing.trader.currency_pairs)
            new_pairs = set(s.trader.currency_pairs)
            if existing_pairs and new_pairs:
                overlap_ratio = len(existing_pairs & new_pairs) / max(1, len(existing_pairs | new_pairs))
                if overlap_ratio > 0.6:
                    overlap = True
                    break

        if not overlap:
            selected.append(s)

    # Verify total exposure doesn't exceed kill switch
    total_lots = sum(s.recommended_lot * max(1, s.trader.max_open_trades) for s in selected)
    if total_lots > 0.30:  # Kill switch limit
        scale_factor = 0.30 / total_lots
        for s in selected:
            s.recommended_lot = max(0.01, round(s.recommended_lot * scale_factor, 2))

    return selected
