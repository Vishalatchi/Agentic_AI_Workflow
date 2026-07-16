import os
from groq import Groq
from app.config import GROQ_AI_API_KEY
client =Groq(
    api_key=GROQ_AI_API_KEY
)

#Defining actual python tool
def calculate_expression(expression:str)->str:
    try:
        return str(eval(expression))
    except Exception as e:
        print(f"Error occurred while calculating the expression{e}")

#Defining JSON Schema
tools_schema =[
    {
        "type":"function",
        "function":{
            "name":"calculate_expression",
            "description" : "A calculator tool to calculate the basic math",
            "parameters": {
                "type":"object",
                "properties":{
                    "expression":{
                        "type":"string",
                        "description":"Solving math expression. e.g.'23 * 43'"
                    }
                },
                "required":["expression"]
            }
        }
    }
]

#OpenAI work flow agentic
def run_openai_agent_workflow(user_prompt:str):
    print(f"user prompt:{user_prompt}")
    messages =[{"role":"user", "content":user_prompt }]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools_schema
    )
    response_message =response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.function.name == "calculate_expression":
                import json
                arguments =json.loads(tool_call.function.arguments)
                expr =arguments.get("expression")
                tool_result =calculate_expression(expr)
                messages.append(response_message)
                messages.append({"role":"tool","tool_call_id":tool_call.id,
                                 "name":"calculate_expression",
                                 "content":tool_result})
            final_response =client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            print(f"calculated result from agentic grok {final_response.choices[0].message.content}")
    else:
        print(f"direct response{response_message.content}")


run_openai_agent_workflow("what is 20  * 10, plus 5 ?")