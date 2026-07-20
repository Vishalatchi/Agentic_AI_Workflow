import random
from langchain_core.tools import tool

#defining tool 1 to identify the status based on order id
@tool (description="A simple tool to identify the order status")
def get_order_status(order_id:str)->str:
    try:
        status=['delayed','delivered','processing','delayed in transit']
        order_status = random.choices(status)
        print(f"Order {order_id} status is {order_status}")
        return order_status
    except Exception as e:
        print(f"Status of this order is having some issue {e}")

#defining tool 2 for refund processing based on order status
@tool (description="A simple tool to identify the order eligibility for refund processing")
def get_order_refund_eligibility(order_id:str, order_status:str)->str:
    eligibility = ""
    try:
        if order_status == "delayed" or order_status =="delayed in transit":
            eligibility = f"Sorry for the incnovenience. Order_id {order_id}eligible for 100% refund"
        else:
            eligibility =f"Your order is within delivery timeline. Refund cannot be processed"
        return eligibility
    except Exception as e:
        print(f"Eligibility of this order for refund processing is having some issue {e}")

#defining tool 3 for escalating to human assistance
@tool (description="A simple tool to escalate the issue for human assistance")
def escalate_to_human(order_id:str,reason:str)->str:
    try:
        return(f"a ticket created for {order_id} for not able to process the refund.{reason}. A human agent will contact the user within 24 hours.")
    except Exception as e:
        print(f" Error occurred while transferring request to customer support person {e}")

