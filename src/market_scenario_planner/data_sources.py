from __future__ import annotations
from typing import Dict, Any, List
import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

def fetch_coingecko_snapshot(symbols: List[str] | None = None) -> Dict[str, Any]:
    """Read-only market snapshot from CoinGecko (public endpoint)."""
    if symbols is None:
        symbols = ["bitcoin", "ethereum", "solana"]
    ids = ",".join(symbols)
    url = f"{COINGECKO_BASE}/simple/price"
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
        "include_market_cap": "true",
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return {"coingecko_simple": r.json(), "symbols": symbols}
