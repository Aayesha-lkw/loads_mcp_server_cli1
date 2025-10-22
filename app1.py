from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from mcp.server.fastmcp import FastMCP
from google.genai import types
import requests
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("loads_fetching", host="0.0.0.0", port=8080, stateless_http=True)
GEMINI_MODEL = "gemini-2.5-flash"
APP_NAME = "app_name1"
USER_ID = "user_id1"
SESSION_ID = "session_id1"
session_service = InMemorySessionService()

input_location_agent = LlmAgent(
    name="InputLocationAgent",
    model=GEMINI_MODEL,
    instruction="""<task>You are an agent that provides latitude and logitude of any given location"<task>.
    <requirement>The values of latitude and longitude should be delivered as float numbers with 4 decimal places.<requirement>
    """,
    description="Agent delivers latitude and logitude values of a given location",
    output_key="query_location"
)
runner_loc = Runner(app_name=APP_NAME, agent=input_location_agent, session_service=session_service)

input_other_agent_prompt = f"""
    You are an Agent that can only answer of user questions related to business and loads in LKW Walter. 
    If question is about getting information about loads schedule or reasoning information of direct or optimal schedule or loads or revenue about loads then output will be "Fetch".
    If questions were asked about LKW Walter then you provide answer using the context provided in the content {context}
    If question is clear but does not make sense then ask user to explain their question.
    If question is irrelevant then ask for relevant questions.
    """
input_other_agent = LlmAgent(
    name="InputOtherAgent",
    model=GEMINI_MODEL,
    instruction= input_other_agent_prompt,
    description="Agent answeres user question according to the input regarding LKW business and loads",
    output_key="query_other"
)
runner_walter = Runner(app_name=APP_NAME, agent=input_other_agent, session_service=session_service)

@mcp.tool()
def optimal_loads(end_lat: float, end_lon:float, end_time: str, start_lat: float, start_lon:float, start_time: str) -> list:
    """
    Gets Optimal Schedule of truck loads from given start and end locations, dates, and times.
    
    Args:
        end_lat : Ending location's latitude
        end_lon : Ending location's longitude
        end_time : Ending location's date and time
        start_lat : Start location's latitude
        start_lon : Start location's longitude
        start_time : Start location's datee and time
    Returns:
        List of all loads that exist in the optimal schedule in a dictionary, each load is provided as its unique identifier, revenue, and arrival date and time, along with total revenue for the entire schedule.
    """

    #xfwd = os.getenv("X-FWD")
    #xauth = os.getenv("X-AUTH")
    #authorization = os.getenv("AUTHORIZATION")

    url = "https://cloud-tunnel.endpoints.wgs-ptv-tools.cloud.goog"

    headers = {
        "X-FWD": "http://evalinno-agentic-ltchat-cmp-preview.dev.lkw-walter.com/evalinno-agentic-ltchat-cmp-preview/api/maximize_revenue",
        "X-AUTH": "wT6vNTkzKXH8E7jOfA5ay4cHGwoJPhOc2XS7UyhVWnQ",
        "Authorization": "Basic YWdlbnRpY19sdGNoYXRfZHM6dkFDMEExdnBLUDlxQldQc0tDWWRCYjQ3",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "end_lat": end_lat,
        "end_lon": end_lon,
        "end_time": end_time,
        "start_lat": start_lat,
        "start_lon": start_lon,
        "start_time": start_time
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        #print(response.json())
        all_loads =  response.json()
        orders_summary = []
        total_revenue = all_loads["total_revenue"]
        for order in all_loads["schedule"]:
            summary = {
                "position_number": order["postion_number"],
                "pickup_address": order["pickup_adr"],
                "pickup_window": f'FROM {order["pickup_rta_from"]} TO {order["pickup_rta_to"]}',
                "delivery_address": order["delivery_adr"],
                "delivery_window": f'FROM {order["delivery_rta_from"]} TO {order["delivery_rta_to"]}',
                "revenue": order["revenue"]
            }
            orders_summary.append(summary)
        orders_summary.append({"total_revenue": total_revenue})
        return orders_summary
        #return response.json()
    else:
        print("Request failed:", response.status_code, response.text)

@mcp.tool()
def direct_loads(date: str, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> list:
    """
    Gets direct loads of trucks from given start and end locations, and starting date.
    
    Args:
        date : Starting date
        start_lat : Start location's latitude
        start_lon : Start location's longitude
        end_lat : Ending location's latitude
        end_lon : Ending location's longitude
            
    Returns:
        List top 5 available direct loads in a list, each load is provided as its unique identifier, revenue, pickup-address, delivery-address, pickup time window, and delivery time window.
    """

    url = "https://cloud-tunnel.endpoints.wgs-ptv-tools.cloud.goog"

    headers = {
        "X-FWD": "http://evalinno-agentic-ltchat-cmp-preview.dev.lkw-walter.com/evalinno-agentic-ltchat-cmp-preview/api/direct_search",
        "X-AUTH": "wT6vNTkzKXH8E7jOfA5ay4cHGwoJPhOc2XS7UyhVWnQ",
        "Authorization": "Basic YWdlbnRpY19sdGNoYXRfZHM6dkFDMEExdnBLUDlxQldQc0tDWWRCYjQ3",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "date": date,
        "end_lat": end_lat,
        "end_lon": end_lon,
        "start_lat": start_lat,
        "start_lon": start_lon
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        all_loads =  response.json()
        orders_summary = []
        for order in all_loads["orders"]:
            summary = {
                "position_number": order["postion_number"],
                "pickup_address": order["pickup_adr"],
                "pickup_window": f'FROM {order["pickup_rta_from"]} TO {order["pickup_rta_to"]}',
                "delivery_address": order["delivery_adr"],
                "delivery_window": f'FROM {order["delivery_rta_from"]} TO {order["delivery_rta_to"]}',
                "revenue": order["revenue"]
            }
            orders_summary.append(summary)
        return orders_summary
    else:
        print("Request failed:", response.status_code, response.text)

@mcp.tool()
async def get_loc_values(user_text:str) -> str:
    """
    This function takes user input and provides respective output
    Input: Takes user question 
    Output: Outputs Answer 
    """
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    full_response_text = []
    async for event in runner_loc.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            response = ''.join([part.text for part in event.content.parts if part.text])
            if response:
                full_response_text.append(response)

    combined_response = '\n\n'.join(full_response_text) if full_response_text else "[No response from agent]"
    return combined_response

@mcp.tool()
async def get_about_walter(user_text:str) -> str:
    """
    This function takes user input and provides respective output
    Input: Takes user question 
    Output: Outputs Answer 
    """
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    content = types.Content(role='user', parts=[types.Part(text=user_text)])
    full_response_text = []
    async for event in runner_walter.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            response = ''.join([part.text for part in event.content.parts if part.text])
            if response:
                full_response_text.append(response)

    combined_response = '\n\n'.join(full_response_text) if full_response_text else "[No response from agent]"
    return combined_response

if __name__ == "__main__":
    mcp.run(transport="streamable-http")