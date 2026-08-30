import gradio as gr
from shopagent import agent

# 5. Launch Gradio ChatInterface with correct message dictionary format for the greeting
gr.ChatInterface(
    fn=agent, 
    title="🛍️ Smart Shop Assistant",
    chatbot=gr.Chatbot(
        value=[
            {"role": "assistant", "content": "👋 Hello! I'm your Smart Shop Assistant. How can I help you find products today?"}
        ]
    )
).launch(share=True)