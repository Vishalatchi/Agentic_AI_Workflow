import os
import httpx
from typing import Annotated,Sequence
from typing_extensions import TypedDict
from app.config import GROQ_AI_API_KEY
from langchain_core.messages import HumanMessage,BaseMessage,SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph,START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition

#state - to maintain messages
class AgentState(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]
#define weather tool
@tool
def get_weather_tool(city:str)->str:
    """Simple weather tool to get current weather condition and temperature."""
    try:
       weather= httpx.get(f"https://api.weatherapi.com/v1/current.json?key=0eba7c73961944a3bcf92927261507&q={city}"
       )
       weather.raise_for_status()
       response = weather.json()
       temp =response["current"]["temp_c"]
       return f"The current temperature in {city} is {temp}C."
    except Exception as e:
        print(f"weather data not available for city{city}. Exception occurred {e}")

#Initialize LLM to bind the tool
llm =ChatGroq(
    temperature = 0,
    model_name= "llama-3.3-70b-versatile",
    groq_api_key = GROQ_AI_API_KEY
)

tools = [get_weather_tool]
llm_with_tools = llm.bind_tools(tools)

#Defining node, step in flowchart
def call_model(state:AgentState):
    messages = state["messages"]
    system_prompt=SystemMessage(content="you are a helpful assistant. Suggest the weather handling for the provided city, refer only the temperature provided. Do not hallucinate.")
    response = llm_with_tools.invoke([system_prompt] + messages)
    return {"messages":[response]}

#Build the graph
workflow=StateGraph(AgentState)
workflow.add_node("agent",call_model)
workflow.add_node("tools",ToolNode(tools))
workflow.add_edge(START,"agent")
workflow.add_conditional_edges("agent",tools_condition)
workflow.add_edge("tools","agent")
app =workflow.compile()
try:
    print("\n--- Graph Architecture Flow ---")
    app.get_graph().print_ascii()
except Exception as e:
    print(f"Could not print ASCII graph: {e}")

# --- Running the Agent ---
if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="get weather handling for chennai today")]}

    # Run the graph and stream the updates
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"\n--- Node '{key}' Output ---")
            print(value)

