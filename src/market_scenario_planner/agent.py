from __future__ import annotations
import json
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from .state import AgentState
from .prompts import (
    INTENT_PARSER_PROMPT,
    SIGNAL_INTERPRETER_PROMPT,
    SCENARIO_PLANNER_PROMPT,
)
from .data_sources import fetch_coingecko_snapshot

load_dotenv()

def _llm() -> ChatOpenAI:
    # Deterministic for evaluations
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

def node_fetch_market_data(state: AgentState) -> AgentState:
    try:
        state.market_data = fetch_coingecko_snapshot()
    except Exception as e:
        state.market_data = {
            "error": str(e),
            "note": "market data unavailable; proceed with generic context"
        }
    return state

def node_parse_intent(state: AgentState) -> AgentState:
    llm = _llm()
    msg = llm.invoke(INTENT_PARSER_PROMPT.format(user_message=state.user_message)).content

    # Robust JSON extraction
    data = {}
    try:
        data = json.loads(msg)
    except Exception:
        start = msg.find("{")
        end = msg.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(msg[start:end+1])

    state.intent = data.get("intent") or "Understand market conditions and plan next steps"
    state.risk_level = (data.get("risk_level") or "medium").lower()
    state.horizon = data.get("horizon") or "1-2 weeks"
    return state

def node_interpret_signals(state: AgentState) -> AgentState:
    llm = _llm()
    state.market_context = llm.invoke(
        SIGNAL_INTERPRETER_PROMPT.format(market_data=json.dumps(state.market_data, indent=2))
    ).content.strip()
    return state

def node_plan(state: AgentState) -> AgentState:
    llm = _llm()
    body = llm.invoke(
        SCENARIO_PLANNER_PROMPT.format(
            market_context=state.market_context or "",
            intent=state.intent or "",
            risk_level=state.risk_level or "",
            horizon=state.horizon or "",
        )
    ).content.strip()

    state.final_answer = _format_final(state, body)
    return state

def _format_final(state: AgentState, body: str) -> str:
    disclaimer = "Disclaimer: informational planning only — not financial advice, no execution."
    header = (
        f"**Market Context**\n{state.market_context or '-'}\n\n"
        f"**User Intent**\n{state.intent or '-'} (risk: {state.risk_level}, horizon: {state.horizon})\n\n"
    )
    return header + body + "\n\n" + disclaimer

def build_graph():
    g = StateGraph(AgentState)

    g.add_node("fetch_market_data", node_fetch_market_data)
    g.add_node("parse_intent", node_parse_intent)
    g.add_node("interpret_signals", node_interpret_signals)
    g.add_node("plan", node_plan)

    g.set_entry_point("fetch_market_data")
    g.add_edge("fetch_market_data", "parse_intent")
    g.add_edge("parse_intent", "interpret_signals")
    g.add_edge("interpret_signals", "plan")
    g.add_edge("plan", END)

    return g.compile()

if __name__ == "__main__":
    app = build_graph()
    user_message = input("User> ").strip()
    state = AgentState(user_message=user_message)
    result = app.invoke(state)
    print("\n" + (result.final_answer or "No output"))
