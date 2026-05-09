import os
import uvicorn
from ag_ui_adk import ADKAgent
from ag_ui_adk.endpoint import add_adk_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.agents import LlmAgent

load_dotenv()

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL")

if LITELLM_BASE_URL:
    from google.adk.models.lite_llm import LiteLlm
    model = LiteLlm(
        model="openai/gpt-4.1",
        api_base=LITELLM_BASE_URL,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
else:
    model = "gemini-2.0-flash"  # uses GOOGLE_API_KEY directly

agent = LlmAgent(
    name="gemini",
    model=model,
    description="A helpful assistant",
    instruction="You are a helpful assistant.",
)

adk_agent = ADKAgent(adk_agent=agent, app_name="gemini")

app = FastAPI()
add_adk_fastapi_endpoint(app=app, agent=adk_agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
