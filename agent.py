# import os
# from dotenv import load_dotenv
# from langgraph.graph import StateGraph, MessagesState
# from langchain_openai import AzureChatOpenAI
# from langchain.schema import AIMessage, HumanMessage, SystemMessage

# load_dotenv()


# # LLM config
# llm = AzureChatOpenAI(
#     azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
#     openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     temperature=0.2,
# )

# # ----------------- SYSTEM PROMPTS -----------------
# SYSTEM_PROMPT_MASTER = """
# You are the Swarm Master, a multi-agent coordinator.
# Responsibilities:
# 1. Classify user intent: Billing, Tech_Support, Account_Management, General_Queries
# 2. Extract entities using NER
# 3. Route the task to the appropriate agent
# """
# SYSTEM_PROMPT_BILLING = "You handle all billing-related queries. Provide actionable solutions."
# SYSTEM_PROMPT_TECH = "You handle all technical support queries. Provide actionable solutions."
# SYSTEM_PROMPT_ACCOUNT = "You handle all account-related queries. Provide actionable solutions."
# SYSTEM_PROMPT_GENERAL = "You answer general queries directly with concise information."

# # ----------------- HELPER FUNCTIONS -----------------
# def llm_node(state, system_prompt: str):
#     messages = state.get("messages", [])
#     prompt_messages = [SystemMessage(content=system_prompt)] + messages
#     result = llm.invoke(prompt_messages)
#     return {"messages": messages + [result]}

# def route_by_intent(state):
#     messages = state.get("messages", [])
#     if not messages:
#         return "General_Agent"
    
#     last_msg = messages[-1]

#     # Get content safely for dict or AIMessage
#     if isinstance(last_msg, AIMessage):
#         last_msg_content = last_msg.content.lower()
#     elif isinstance(last_msg, dict):
#         last_msg_content = last_msg.get("content", "").lower()
#     else:
#         last_msg_content = str(getattr(last_msg, "content", "")).lower()
    
#     if any(word in last_msg_content for word in ["invoice", "billing", "charged", "payment"]):
#         return "Billing_Agent"
#     elif any(word in last_msg_content for word in ["internet", "connection", "wifi", "router"]):
#         return "TechSupport_Agent"
#     elif any(word in last_msg_content for word in ["account", "email", "username"]):
#         return "Account_Agent"
#     else:
#         return "General_Agent"


# def extract_ai_response(messages):
#     if not messages:
#         return "No response generated."
#     for msg in reversed(messages):
#         if isinstance(msg, list):
#             res = extract_ai_response(msg)
#             if res != "No response generated.":
#                 return res
#         elif isinstance(msg, AIMessage):
#             return msg.content
#         elif isinstance(msg, HumanMessage):
#             continue
#         elif isinstance(msg, dict):
#             if msg.get("role") == "assistant":
#                 return msg.get("content", "No response generated.")
#             elif "content" in msg:
#                 return msg["content"]
#         elif hasattr(msg, "content"):
#             return getattr(msg, "content", "No response generated.")
#     return "No response generated."

# # ----------------- CREATE SWARM STATEGRAPH -----------------
# graph = StateGraph(dict)  # Use dict-based state

# graph.add_node("Swarm_Master", lambda s: llm_node(s, SYSTEM_PROMPT_MASTER))
# graph.add_node("Billing_Agent", lambda s: llm_node(s, SYSTEM_PROMPT_BILLING))
# graph.add_node("TechSupport_Agent", lambda s: llm_node(s, SYSTEM_PROMPT_TECH))
# graph.add_node("Account_Agent", lambda s: llm_node(s, SYSTEM_PROMPT_ACCOUNT))
# graph.add_node("General_Agent", lambda s: llm_node(s, SYSTEM_PROMPT_GENERAL))

# graph.set_entry_point("Swarm_Master")

# graph.add_conditional_edges(
#     "Swarm_Master",
#     route_by_intent,
#     path_map=["Billing_Agent", "TechSupport_Agent", "Account_Agent", "General_Agent"]
# )

# graph.set_finish_point("Billing_Agent")
# graph.set_finish_point("TechSupport_Agent")
# graph.set_finish_point("Account_Agent")
# graph.set_finish_point("General_Agent")

# swarm_app = graph.compile()

# # ----------------- FUNCTION TO RUN CONVERSATION -----------------
# def run_swarm_conversation(query: str) -> str:
#     state = {"messages": [{"role": "user", "content": query}]}
#     result_state = swarm_app.invoke(state)
#     messages = result_state.get("messages", [])
#     return extract_ai_response(messages)










import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

load_dotenv()

print("MODEL =", os.getenv("GEMINI_MODEL"))
print("API KEY PREFIX =", os.getenv("GEMINI_API_KEY")[:15])

# ──────────────────────────────────────────────
# LLM config — Gemini
# ──────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    convert_system_message_to_human=True,
)

# ──────────────────────────────────────────────
# SYSTEM PROMPTS
# ──────────────────────────────────────────────
SYSTEM_PROMPT_MASTER = """
You are the Swarm Master, a multi-agent coordinator.

Responsibilities:
1. Classify user intent.
2. Extract relevant entities.
3. Route the request to the appropriate agent.

These steps are internal only.
Never reveal:
- Intent classification
- Extracted entities
- Routing decisions
- Agent names

Return only the final user-facing response.
"""
SYSTEM_PROMPT_BILLING = "You handle all billing-related queries. Provide actionable solutions."
SYSTEM_PROMPT_TECH    = "You handle all technical support queries. Provide actionable solutions."
SYSTEM_PROMPT_ACCOUNT = "You handle all account-related queries. Provide actionable solutions."
SYSTEM_PROMPT_GENERAL = "You answer general queries directly with concise information."


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def llm_node(state: dict, system_prompt: str) -> dict:
    messages = state.get("messages", [])
    prompt_messages = [SystemMessage(content=system_prompt)] + messages
    result = llm.invoke(prompt_messages)
    return {"messages": messages + [result]}


def route_by_intent(state: dict) -> str:
    """Route based on the original USER message (index 0)."""
    messages = state.get("messages", [])
    if not messages:
        return "General_Agent"

    user_msg = messages[0]

    if isinstance(user_msg, HumanMessage):
        content = user_msg.content.lower()
    elif isinstance(user_msg, dict):
        content = user_msg.get("content", "").lower()
    else:
        content = str(getattr(user_msg, "content", "")).lower()

    if any(word in content for word in ["invoice", "billing", "charged", "payment", "refund", "fee"]):
        return "Billing_Agent"
    elif any(word in content for word in ["internet", "connection", "wifi", "router", "network", "speed", "outage"]):
        return "TechSupport_Agent"
    elif any(word in content for word in ["account", "email", "username", "password", "login", "profile"]):
        return "Account_Agent"
    else:
        return "General_Agent"


def extract_ai_response(messages: list) -> str:
    """Return the latest non-empty AI response, skipping user messages."""
    if not messages:
        return "No response generated."

    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = (msg.content or "").strip()
            if content:
                return content
        elif isinstance(msg, dict):
            if msg.get("role") == "assistant":
                content = (msg.get("content") or "").strip()
                if content:
                    return content

    return "No response generated."


# ──────────────────────────────────────────────
# BUILD SWARM STATEGRAPH
# ──────────────────────────────────────────────
graph = StateGraph(dict)

graph.add_node("Swarm_Master",      lambda s: llm_node(s, SYSTEM_PROMPT_MASTER))
graph.add_node("Billing_Agent",     lambda s: llm_node(s, SYSTEM_PROMPT_BILLING))
graph.add_node("TechSupport_Agent", lambda s: llm_node(s, SYSTEM_PROMPT_TECH))
graph.add_node("Account_Agent",     lambda s: llm_node(s, SYSTEM_PROMPT_ACCOUNT))
graph.add_node("General_Agent",     lambda s: llm_node(s, SYSTEM_PROMPT_GENERAL))

graph.set_entry_point("Swarm_Master")

graph.add_conditional_edges(
    "Swarm_Master",
    route_by_intent,
    path_map={
        "Billing_Agent":     "Billing_Agent",
        "TechSupport_Agent": "TechSupport_Agent",
        "Account_Agent":     "Account_Agent",
        "General_Agent":     "General_Agent",
    }
)

graph.set_finish_point("Billing_Agent")
graph.set_finish_point("TechSupport_Agent")
graph.set_finish_point("Account_Agent")
graph.set_finish_point("General_Agent")

swarm_app = graph.compile()


# ──────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ──────────────────────────────────────────────
def run_swarm_conversation(query: str) -> str:
    state = {"messages": [HumanMessage(content=query)]}
    result_state = swarm_app.invoke(state)
    messages = result_state.get("messages", [])
    return extract_ai_response(messages)


# ──────────────────────────────────────────────
# LOCAL TEST
# ──────────────────────────────────────────────
if __name__ == "__main__":
    query = "What is the difference between cement and concrete?"
    print("=" * 60)
    response = run_swarm_conversation(query)
    print("Q:", query)
    print("A:", response)