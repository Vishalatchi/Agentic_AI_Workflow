from langchain_groq import ChatGroq
from app.config import GROQ_AI_API_KEY
from app.AI_Programs.ecommerce_agentic_workflow import tools

#llm model
llm = ChatGroq(
    temperature = 0,
    model_name= "llama-3.3-70b-versatile",
    groq_api_key=GROQ_AI_API_KEY
)

tools_list =[tools.get_order_status,tools.get_order_refund_eligibility,tools.escalate_to_human]
llm_with_tools = llm.bind_tools(tools_list)



