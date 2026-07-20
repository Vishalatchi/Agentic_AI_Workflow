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

@tool (description="finding packing details")
def suggest_packing_list(temperature: str) -> str:
    import re
    """Suggests what items or clothing to pack based on a given temperature in Celsius."""
    temp = re.findall(r"[-+]?\d*\.\d+|\d+", temperature)
    temp=float(temp[0])
    if temp > 28:
        return "It's hot! Pack shorts, t-shirts, sunglasses, sunscreen, and a water bottle."
    elif 15 <= temp <= 28:
        return "Pleasant weather. Pack jeans, light layers, a light jacket for evenings, and comfortable walking shoes."
    else:
        return "It's chilly. Pack a heavy coat, sweaters, a scarf, and warm socks."

#Initialize LLM to bind the tool
llm =ChatGroq(
    temperature = 0,
    model_name= "llama-3.3-70b-versatile",
    groq_api_key = GROQ_AI_API_KEY
)

tools = [get_weather_tool,suggest_packing_list]
llm_with_tools = llm.bind_tools(tools)

#Defining node, step in flowchart
def call_model(state:AgentState):
    messages = state["messages"]
    system_prompt=SystemMessage(content=""
            "You are a helpful travel assistant.\n"
            "When asked about the weather and packing suggestions:\n"
            "1. First, call 'get_weather_tool' to fetch the temperature.\n"
            "2. Once you have the temperature, immediately call 'suggest_packing_list' using that temperature.\n"
            "3. Finally, combine both tool outputs into a friendly message. Do not make up packing recommendations without calling the packing tool.""")
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
   # for output in app.stream(inputs):
    #    for key, value in output.items():
     #       print(f"\n--- Node '{key}' Output ---")
      #      print(value)
    final_response = app.invoke(inputs)
    final_ans = final_response["messages"][-1]
    print(final_ans.content)

