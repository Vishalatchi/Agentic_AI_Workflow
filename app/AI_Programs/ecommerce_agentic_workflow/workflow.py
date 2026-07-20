from langgraph.graph import StateGraph,START
from langgraph.prebuilt import tools_condition
from app.AI_Programs.ecommerce_agentic_workflow.state import AgentState
from app.AI_Programs.ecommerce_agentic_workflow.nodes import call_model
from app.AI_Programs.ecommerce_agentic_workflow.llm import tools_list
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

#Initialize the graph with state
workflow = StateGraph(AgentState)
#Add agent and tools node
workflow.add_node("agent",call_model)
workflow.add_node('tools',ToolNode(tools_list))
#define links/edges
workflow.add_edge(START,"agent")
workflow.add_conditional_edges("agent",tools_condition)
workflow.add_edge("tools","agent")
#add memory saver for conversational persistence
memory= MemorySaver()

#compile graph with short-circuit human interrupt
#it tells langgraph : if the next step is running a tool, pause first so we can check it.
app = workflow.compile(checkpointer=memory)

#running the agent

# --- EXECUTION SIMULATION ---
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "customer_session_200"}}

    print("--- STEP 1: Sending request that forces an escalation tool call ---")
    inputs = {"messages": [HumanMessage(content="My order 12345 is delayed in transit. I want a refund now!")]}

    # Run the graph. It will stop inside the node when it hits `interrupt()`
    result = app.invoke(inputs, config)

    # Highlight: Check if the graph execution paused on an inline interrupt
    if "__interrupt__" in result:
        print(f"\n🛑 GRAPH INTERRUPTED SUCCESSFULLY!")
        print(f"Message from graph: {result['__interrupt__'][0].value}")

        print("\n--- STEP 2: Simulating Human Input / Admin Approval ---")
        # To resume, call invoke again passing a Command(resume=...) object
        # The string "Approved by Supervisor" becomes the return value of the interrupt() function inside the node
        final_result = app.invoke(Command(resume="Approved by Supervisor"), config)

        print("\n--- Final Assistant Answer After Human Handoff ---")
        print(final_result["messages"][-1].content)
    else:
        print("\nGraph finished completely without interrupting.")
        print(result["messages"][-1].content)
