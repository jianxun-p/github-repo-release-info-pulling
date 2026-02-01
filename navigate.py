from openai import OpenAI
from utils import *
import json
from time import sleep
import sys
import os
from math import ceil
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

move_box_tools = [
    {
        "type": "function",
        "function": {
            "name": "translate_box_down",
            "description": "Move red shaded rectangle to the down",
            "parameters": {},
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_box_up",
            "description": "Move red shaded rectangle to the up",
            "parameters": {},
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_box_left",
            "description": "Move red shaded rectangle to the left",
            "parameters": {},
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_box_right",
            "description": "Move red shaded rectangle to the right",
            "parameters": {},
            "additionalProperties": False
        }
    }
]

save_output_tools = [
    {
        "type": "function",
        "function": {
            "name": "save_output",
            "description": "Saves repository metadata extracted from the image",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "the repository (e.g. openclaw/openclaw)"},
                    "version": {"type": "string", "description": "The version number (e.g., v2026.1.29)"},
                    "tag": {"type": "string", "description": "The release tag (e.g. 77e703c)"},
                    "author": {"type": "string", "description": "The username of the author (e.g. steipete)"}
                },
                "required": ["repo", "version", "tag", "author"],
                "additionalProperties": False
            }
        }
    }
]

api_key="hi"

model = "gpt-4.1-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

msgs = []

def reason_contained(prompt, img="boxed_screenshot.png"):
    global msgs
    msgs = []
    msgs.append({
            "role": "user",
            "content": [
                { "type": "text", "text": prompt },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(img)}"
                    },
                },
            ],
        })
    response = client.chat.completions.create(model=model, messages=msgs)
    print(prompt)
    print(response.choices[0].message)
    res_msg = response.choices[0].message.content
    msgs.append(response.choices[0].message)
    return "yes" in res_msg.lower()



def save_output(repo: str, version: str, tag: str, author: str):
    global task_complete
    with open("output.json", 'wt') as f:
        json.dump(
            {
                "repository": repo, 
                "latest_release": [
                    {
                        "version": version,
                        "tag": tag,
                        "author": author
                    }
                ]
            }, 
            f
        )

def scroll_down():
    global box_pos
    page.mouse.wheel(0, height)
    page.screenshot(path=screenshot_path, full_page=False)
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

def translate_box_right():
    global box_pos
    box_pos[0] += box_pos[2]# // 2
    box_pos[0] = min(width - box_pos[2], box_pos[0])
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

def translate_box_left():
    global box_pos
    box_pos[0] -= box_pos[2]# // 2
    box_pos[0] = max(0, box_pos[0])
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

def translate_box_down():
    global box_pos
    box_pos[1] += box_pos[3]# // 2
    box_pos[1] = min(height - box_pos[3], box_pos[1])
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

def translate_box_up():
    global box_pos
    box_pos[1] -= box_pos[3]# // 2
    box_pos[1] = max(0, box_pos[1])
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)




def zoom_box():
    box_pos[2] = ceil(box_pos[2] / 2)
    box_pos[3] = ceil(box_pos[3] / 2)
    # box_pos[2] *= 2
    # box_pos[3] *= 2
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

def zoom_out():
    box_pos[2] = min(box_pos[2] * 2, width)
    box_pos[3] = min(box_pos[3] * 2, height)
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

tools_map = {
    "translate_box_right": translate_box_right,
    "translate_box_left": translate_box_left,
    "translate_box_up": translate_box_up,
    "translate_box_down": translate_box_down,
    "save_output": save_output
}

def call_tool(res_msg):
    global input_messages
    if not res_msg.tool_calls:
        return
    for call in res_msg.tool_calls:
        name = call.function.name
        args = json.loads(call.function.arguments)
        print(f"called tool: {name}({args})")
        if name not in tools_map:
            print(f"bad tool: {name}({args})")
        tools_map[name](**args)
        msgs.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": "Ok"
        })

def reason_dir(prompt, img="boxed_screenshot.png"):
    global msgs
    msgs.append({
            "role": "user",
            "content": [
                { "type": "text", "text": prompt },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(img)}"
                    },
                },
            ],
        })
    response = client.chat.completions.create(model=model, messages=msgs, tools=move_box_tools, tool_choice="required")
    print(prompt)
    print(response.choices[0].message)
    res_msg = response.choices[0].message
    msgs.append(res_msg)
    return call_tool(res_msg)

def save_info(prompt, img="screenshot.png"):
    global msgs
    msgs.append({
            "role": "user",
            "content": [
                { "type": "text", "text": prompt },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(img)}"
                    },
                },
            ],
        })
    response = client.chat.completions.create(model=model, messages=msgs, tools=save_output_tools, tool_choice="required")
    print(prompt)
    print(response.choices[0].message)
    res_msg = response.choices[0].message
    msgs.append(res_msg)
    return call_tool(res_msg)

def locate_x(goal, target, accuracy=120):
    global box_pos, width, height
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

    accurate_enough = box_pos[2] < accuracy
    found = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if accurate_enough and found:
        print(f"located: {target}")
        return
    if found:
        box_pos[2] = ceil(box_pos[2] / 2)
        draw_box("boxed_screenshot.png", screenshot_path, box_pos)
    else:
        box_pos[0] = max(0, box_pos[0] - box_pos[2])
        box_pos[2] = min(box_pos[2] * 4, width)
        draw_box("boxed_screenshot.png", screenshot_path, box_pos)
    contained1 = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if contained1:
        return
    translate_box_right()
    contained2 = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if contained2:
        return
    translate_box_left()

def locate_y(goal, target, accuracy=50):
    global box_pos, width, height
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)

    accurate_enough = box_pos[3] < accuracy
    found = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if accurate_enough and found:
        print(f"located: {target}")
        return
    if found:
        box_pos[3] = ceil(box_pos[3] / 2)
        draw_box("boxed_screenshot.png", screenshot_path, box_pos)
    else:
        box_pos[1] = max(0, box_pos[1] - box_pos[3])
        box_pos[3] = min(box_pos[3] * 4, height)
        draw_box("boxed_screenshot.png", screenshot_path, box_pos)
    contained2 = True
    contained1 = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if contained1:
        return
    translate_box_down()
    contained2 = reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png")
    if contained2:
        return
    translate_box_up()



def locate(goal, target, accuracy=(120, 40)):
    global box_pos, width, height
    box_pos = [0, 0, width, height]
    page.screenshot(path=screenshot_path, full_page=False)
    draw_box("boxed_screenshot.png", screenshot_path, box_pos)
    while not reason_contained(f"{goal}\nIs {target} on screen? yes or no (don't explain)", "croped.png"):
        scroll_down()

    while box_pos[2] > accuracy[0] or box_pos[3] > accuracy[1]:
        locate_x(goal, target, accuracy[0])
        locate_y(goal, target, accuracy[1])


def click():
    page.mouse.click(box_pos[0] + box_pos[2] // 2, box_pos[1] + box_pos[3] // 2)


if __name__ == '__main__':

    repo = sys.argv[1]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        page.goto(url)

        locate("I want to search up repo {repo}", "search button", (50, 50))
        click()
        sleep(1)

        page.keyboard.insert_text(repo)
        page.keyboard.press("Enter")
        sleep(1)

        locate(f"Search repo '{repo}'", "{repo} repo")
        click()
        sleep(1)

        locate("Get information about the latest releases", f"latest {repo} release")
        click()
        sleep(1)

        page.screenshot(path=screenshot_path, full_page=True)
        save_info("Get information about the latest release", screenshot_path)
        sleep(1)


