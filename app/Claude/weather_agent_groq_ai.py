import os
from groq import Groq
from app.config import GROQ_AI_API_KEY
from fastapi import APIRouter
import httpx


router=APIRouter()
client =Groq(
    api_key=GROQ_AI_API_KEY
)

#define weather tool
@router.get("/weather")
def get_weather_tool(city:str)->str:
    try:
       weather= httpx.get(f"https://api.weatherapi.com/v1/current.json?key=0eba7c73961944a3bcf92927261507&q={city}"
       )
       weather.raise_for_status()
       response = weather.json()
       temp =response["current"]["temp_c"]
       return temp
    except Exception as e:
        print(f"weather data not available for city{city}. Exception occurred {e}")


#defining tool_schema
tool_schema=[
    {
   "type": "function",
    "function":{
    "name":"get_weather_tool",
    "description":"Simple weather tool to get current weather condition",
    "parameters":{
        "type":"object",
        "properties":
            {
                "city":
                    {
                    "type":"string",
                    "description":"name of the city to know the temperature for"
                }
            }
        },
        "required":["city"]
    }
    }
]

#defining agentic ai to decide and show details of weather
def run_agentic_weather_tool(user_prompt:str):
    message =[{ "role":"user", "content":user_prompt}]
    response =client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=message,
            tools=tool_schema
            )
    responses=response.choices[0].message
    tools_use= responses.tool_calls
    if tools_use:
       for tool_call in tools_use:
           if tool_call.function.name=="get_weather_tool":
               import json
               arguments = json.loads(tool_call.function.arguments)
               print(arguments)
               city = arguments.get("city")
               temperature = get_weather_tool(city)
               message.append(responses)
               message.append({
                   "role":"user",
                   "content":f"Suggest the weather handling for {city} with temperature {temperature}. Do not hallucinate"
               })
               final_response=client.chat.completions.create(
                   model="llama-3.3-70b-versatile",
                   messages=message
               )
               print(final_response.choices[0].message)


run_agentic_weather_tool("get weather handling for chennai today")