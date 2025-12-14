from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    # user input
    user_message: str

    # extracted intent
    intent: Optional[str] = None
    risk_level: Optional[str] = None  # low / medium / high
    horizon: Optional[str] = None     # e.g., "7 days", "1 month"

    # market data (read-only)
    market_data: Dict[str, Any] = Field(default_factory=dict)

    # interpreted signals
    market_context: Optional[str] = None
    scenarios: List[str] = Field(default_factory=list)

    # final formatted response
    final_answer: Optional[str] = None
