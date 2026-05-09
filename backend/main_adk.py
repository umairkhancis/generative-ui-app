import uvicorn
from ag_ui_adk import ADKAgent
from ag_ui_adk.endpoint import add_adk_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.agents import LlmAgent

load_dotenv()

agent = LlmAgent(
    name="gemini",
    model="gemini-2.0-flash",
    description="A helpful assistant",
    instruction="You are a helpful assistant.",
)

adk_agent = ADKAgent(adk_agent=agent, app_name="gemini")

app = FastAPI()
add_adk_fastapi_endpoint(app=app, agent=adk_agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
