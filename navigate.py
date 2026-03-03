from langgraph.graph import END, StateGraph
from openai import OpenAI
from tool import CLASS_TOOL_ATTR, CLASS_TOOL_MAP_ATTR
from utils import *
import json
import os
from browser import Browser
# from playwright.sync_api import Browser, sync_playwright
from dotenv import load_dotenv
from typing import TypedDict, List, Optional

load_dotenv()
model = "gpt-4.1"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
url = "https://github.com"

system_prompt = """
You are a web navigation agent. 
Your task is to navigate the web page to achieve the given goal. 
You can use the provided tools (Playwright) to interact with the web page. 
Always think step by step and use the tools to observe the web page before taking any action.
"""

browser = Browser()

def screenshot_path(step):
    return f"screenshot_{step}.png"

def llm(goal, screenshot_path = None, messages = [{"role": "system", "content": system_prompt}]):
    """
    Generate a response from the LLM based on the goal and screenshot.
    @param goal: The navigation goal or instruction for the agent.
    @param screenshot_path: The file path to the screenshot image to be included in the prompt
    @return: The response from the LLM, which may include tool calls or actions to be taken by the agent.
    """
    if screenshot_path:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Goal: {goal}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(screenshot_path)}"
                    }
                },
            ],
        })

    response = client.chat.completions.create(
        model=model,
        # response_format={"type": "json_object"},
        tools=getattr(Browser, CLASS_TOOL_ATTR),
        # tool_choice="required"
        messages=messages
    )
    return response.choices[0].message

def call_tools(response_message):
    """
    dispatches the function calling
    """
    if not response_message.tool_calls:
        return
    msgs = []
    for call in response_message.tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments)
        msgs.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(getattr(browser, name)(**args))
        })
    return msgs


class AgentState(TypedDict):
    goal: str
    screenshot_count: int
    messages: dict
    observation: Optional[str]
    steps: int


def observe(state: AgentState):
    state["screenshot_count"] += 1
    path = browser.screenshot(screenshot_path(state["screenshot_count"]))
    return {**state, "screenshot_count": state["screenshot_count"]}

def think(state: AgentState):
    messages = llm(state["goal"], screenshot_path=screenshot_path(state["screenshot_count"]))
    return {**state, "messages": messages}

def act(state: AgentState):
    messages = state["messages"]
    tool_msgs = call_tools(messages)
    messages += tool_msgs
    return {**state, "messages": llm(state["goal"], screenshot_path=screenshot_path(state["screenshot_count"]), messages=messages)}

def should_continue(state: AgentState):
    if state["steps"] > 10:
        return END
    return "observe"



graph = StateGraph(AgentState)

graph.add_node("observe", observe)
graph.add_node("think", think)
graph.add_node("act", act)

graph.set_entry_point("observe")

graph.add_edge("observe", "think")
graph.add_edge("think", "act")
graph.add_conditional_edges("act", should_continue)

app = graph.compile()


if __name__ == '__main__':

    # repo = sys.argv[1]

    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=False, slow_mo=500)
    #     page = browser.new_page()
    #     page.goto(url)
    #     sleep(1)
    browser.goto(url)

    result = app.invoke({
        "goal": "Click the search button",
        "screenshot_count": 0,
        "action": None,
        "observation": None,
        "steps": 0
    })


