from langgraph.graph import END, START, StateGraph

from agent.nodes.compose_answer import compose_answer
from agent.nodes.select_query import select_query
from agent.nodes.run_catalog_query import run_catalog_query
from agent.nodes.document_search import search_documents
from agent.nodes.intent import recognize_intent
from agent.nodes.refuse import refuse
from agent.nodes.sql_query import run_sql_query
from agent.state import AgentState

def route_after_intent(state: AgentState) -> str:
    match state["intent"].intent:
        case "security_breach" | "out_of_scope":
            return "refuse"
        case "document_search":
            return "search_documents"
        case "northwind_query":
            return "select_query"
        # case "reporting":
        #     return "compose_answer"
        case other:
            raise ValueError(f"Unexpected intent: {other}")
        
def route_after_selection(state: AgentState) -> str:
    if state.get("query_selection"):
        return "run_catalog_query"
    else:
        return "run_sql_query"
    
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("recognize_intent", recognize_intent)
    builder.add_node("refuse", refuse)
    builder.add_node("select_query", select_query)
    builder.add_node("run_catalog_query", run_catalog_query)
    builder.add_node("run_sql_query", run_sql_query)
    builder.add_node("search_documents", search_documents)
    builder.add_node("compose_answer", compose_answer)

    builder.add_edge(START, "recognize_intent")
    builder.add_conditional_edge
    (
        "recognize_intent", 
        route_after_intent,
        {
            "refuse": "refuse",
            "search_documents": "search_documents", 
            "select_query": "select_query"
        },
    )
    builder.add_edge("run_catalog_query", "compose_answer")
    builder.add_edge("run_sql_query", "compose_answer")
    builder.add_edge("search_documents", "compose_answer")
    builder.add_edge("compose_answer", END)
    builder.add_edge("refuse", END)
    return builder.compile()