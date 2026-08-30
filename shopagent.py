import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

PRICES = {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699}

def get_price(item):
    print(f"🔧 tool called: get_price({item})")
    price = PRICES.get(item.lower())
    if price is None:
        return "unknown"
    return f"₹{price}"

tools = [{
    "type": "function",                                    
    "function": {
        "name": "get_price",                                   
        "description": "Get the price of a shop item the user asks about.",
        "parameters": {                                    
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]

def agent(message, history):
    # 1. Map Gradio's new dictionary history format to OpenAI format
    messages = []
    for turn in history:
        # Gradio messages format uses dictionaries with 'role' and 'content'
        if isinstance(turn, dict):
            messages.append({"role": turn["role"], "content": turn["content"]})
        elif isinstance(turn, (list, tuple)) and len(turn) == 2:
            # Fallback just in case history contains pairs
            user_msg, assistant_msg = turn
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
            
    # 2. Append current user message
    messages.append({"role": "user", "content": message})

    # 3. Initial LLM call
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", messages=messages, tools=tools
    )
    msg = response.choices[0].message

    # 4. Handle tool calls
    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            item_name = args["item"]
            result = get_price(item_name)
            
            # Append tool result
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
            
            # Fallback text if item is not found in catalog
            if result == "unknown":
                messages.append({
                    "role": "system", 
                    "content": f"The item '{item_name}' is not available in our catalog. Can I help you with something else?"
                })
            
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", messages=messages
        )
        msg = response.choices[0].message

    return msg.content

