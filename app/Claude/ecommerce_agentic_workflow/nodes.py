from app.Claude.ecommerce_agentic_workflow.state import AgentState
from app.Claude.ecommerce_agentic_workflow.llm import llm_with_tools
from langchain_core.messages import SystemMessage
from langgraph.types import interrupt
#defining nodes, steps in flowchart
def call_model(state:AgentState):
    try:
        user_prompt =state["messages"]
        print(user_prompt)
        system_prompt=SystemMessage(content = ""
                        "you are a helpful assistant. identify the order status based on order id provided by user"
                        "1. First get the order_id from user request"
                        "2. Use the tool get_order_status to get the status of the order"
                        "3. Use the tool get_order_refund_eligibility to get the eligibility for thd refund if the user request for cancel and refund"
                        "4. If the order is eligible for refund, use tool escalate_to_human to escalate the issue to human assistance, otherwise skip this tool use"
                        "5. Finally combine all the tool responses and provide friendly message to the user. "
                        "6. Do not make up status and refund eligibility or escalation without calling the tools"
                        "7. Do not hallucinate"
                        "")
        response = llm_with_tools.invoke([system_prompt]+user_prompt)
        # Check if the LLM generated tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "escalate_to_human":
                    print(f"\n[Node Log] LLM requested escalation tool. Triggering interrupt...")

                    # Graph stops right here. The string we pass is sent to the client.
                    human_decision = interrupt("Human authorization needed to escalate this order.")

                    print(f"[Node Log] Graph Resumed! Human decision received: {human_decision}")

        return {"messages": [response]}
    except Exception as e:
        print(f"Issue in calling the model with user and system prompt. {e}")