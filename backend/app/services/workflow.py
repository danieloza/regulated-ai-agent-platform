from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph


class AgentRunState(TypedDict, total=False):
    question: str
    policy_decision: str
    context_count: int
    tool_name: str
    approval_status: str
    answer: str
    trace: list[str]


WORKFLOW_NODES = [
    "classify_request",
    "retrieve_context",
    "policy_check",
    "tool_call",
    "human_approval",
    "final_answer",
]


def _append(state: AgentRunState, node: str) -> AgentRunState:
    trace = [*state.get("trace", []), node]
    return {**state, "trace": trace}


def classify_request(state: AgentRunState) -> AgentRunState:
    return _append(state, "classify_request")


def retrieve_context(state: AgentRunState) -> AgentRunState:
    return _append(state, "retrieve_context")


def policy_check(state: AgentRunState) -> AgentRunState:
    return _append(state, "policy_check")


def tool_call(state: AgentRunState) -> AgentRunState:
    return _append(state, "tool_call")


def human_approval(state: AgentRunState) -> AgentRunState:
    return _append(state, "human_approval")


def final_answer(state: AgentRunState) -> AgentRunState:
    return _append(state, "final_answer")


def should_request_approval(state: AgentRunState) -> str:
    return "approval" if state.get("policy_decision") == "approval_required" else "final"


def build_regulated_agent_graph():
    graph = StateGraph(AgentRunState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("policy_check", policy_check)
    graph.add_node("tool_call", tool_call)
    graph.add_node("human_approval", human_approval)
    graph.add_node("final_answer", final_answer)
    graph.set_entry_point("classify_request")
    graph.add_edge("classify_request", "retrieve_context")
    graph.add_edge("retrieve_context", "policy_check")
    graph.add_edge("policy_check", "tool_call")
    graph.add_conditional_edges(
        "tool_call",
        should_request_approval,
        {"approval": "human_approval", "final": "final_answer"},
    )
    graph.add_edge("human_approval", "final_answer")
    graph.add_edge("final_answer", END)
    return graph.compile()


REGULATED_AGENT_GRAPH = build_regulated_agent_graph()


def run_workflow_trace(policy_decision: str, context_count: int) -> list[str]:
    result = REGULATED_AGENT_GRAPH.invoke(
        {
            "policy_decision": policy_decision,
            "context_count": context_count,
            "trace": [],
        }
    )
    return result["trace"]
