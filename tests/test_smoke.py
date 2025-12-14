from market_scenario_planner.agent import build_graph
from market_scenario_planner.state import AgentState

def test_smoke():
    app = build_graph()
    out = app.invoke(AgentState(user_message="I want to preserve capital for 7 days, low risk."))
    assert out.final_answer
    assert "Disclaimer" in out.final_answer
