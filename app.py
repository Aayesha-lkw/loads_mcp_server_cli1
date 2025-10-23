from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mcp.server.fastmcp import FastMCP
import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("loads_fetching", host="0.0.0.0", port=8080, stateless_http=True)
GEMINI_MODEL = "gemini-2.5-flash"
APP_NAME = "app_name1"
USER_ID = "user_id1"
SESSION_ID = "session_id1"
session_service = InMemorySessionService()

df = pd.read_csv("output.csv")
context = df.iloc[0].to_dict()

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
root_agent = input_other_agent
runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

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
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            response = ''.join([part.text for part in event.content.parts if part.text])
            if response:
                full_response_text.append(response)

    combined_response = '\n\n'.join(full_response_text) if full_response_text else "[No response from agent]"
    return combined_response





if __name__ == "__main__":
    mcp.run(transport="streamable-http")