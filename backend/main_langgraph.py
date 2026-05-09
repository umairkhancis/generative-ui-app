import uvicorn
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HOST = "0.0.0.0"
PORT = 8000
MODEL = "gpt-4.1"

SYSTEM_PROMPT = (
    "You are a helpful assistant for a demo app with a few available UI tools. "
    "Prefer using a matching frontend tool when it would present the answer clearly. "
    "For chart requests, use concise made-up demo data when the user does not provide data. "
    "Use pieChart for category distributions "
    "and flightCard for a single flight summary when relevant. "
    "Tool arguments must match the provided schema exactly."
)

graph = create_agent(
    model=ChatOpenAI(model=MODEL),
    tools=[],
    middleware=[CopilotKitMiddleware()],
    checkpointer=MemorySaver(),
    system_prompt=SYSTEM_PROMPT,
)

agent = LangGraphAGUIAgent(
    name="lesson2_agent",
    description="Lesson 2 chart agent",
    graph=graph,
)

app = FastAPI()
add_langgraph_fastapi_endpoint(app=app, agent=agent, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
