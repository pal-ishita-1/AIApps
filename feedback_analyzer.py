import json
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Preset Dummy Data for quick testing
DUMMY_TICKETS = """1. "App crashes every time I open the checkout screen on iOS 18. I was trying to buy a gift for a birthday today! Very frustrated."
2. "I love the new dark mode theme! It looks sleek and saves battery. Great update team."
3. "My package (#8921) was supposed to arrive two days ago. Tracking hasn't updated and customer support phone line keeps disconnecting me. Urgent help needed!"
4. "Would be awesome if you could add a wishlist feature so I can save items for later sales."
5. "The sizing on the medium shirt is much smaller than described. Returning it tomorrow."
"""

def get_dummy_data():
    """Returns preset dummy customer tickets."""
    return DUMMY_TICKETS

def analyze_and_triage_feedback(raw_feedback: str):
    """
    Processes raw feedback via Groq using the OpenAI SDK wrapper.
    """
    if not raw_feedback.strip():
        return pd.DataFrame(), "Please input customer feedback or click 'Load Dummy Data'."

   
    # Initialize standard OpenAI client pointing to Groq's endpoint
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    system_prompt = """
    You are an AI Operations & Support Analyst. 
    Analyze the provided customer reviews/tickets and extract structured information.
    
    For each distinct ticket/feedback entry, extract:
    1. Ticket ID / Summary (Brief phrase summarizing the issue)
    2. Category (Choose one: Bug Report, Feature Request, Logistics/Shipping, General Feedback, Sizing/Product Quality)
    3. Sentiment (Positive, Neutral, Negative)
    4. Escalation Needed (Yes/No - set to 'Yes' for severe bugs, missed deliveries, angry tone, or blocking issues)
    5. Priority (Urgent, High, Medium, Low)
    6. Suggested Response (A professional 1-2 sentence response template for the support rep)

    Return ONLY a valid JSON array of objects with the following exact keys:
    ["ticket_summary", "category", "sentiment", "escalation_needed", "priority", "suggested_response"]
    """

    try:
        # Call Groq models through the OpenAI client
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Feedback to analyze:\n{raw_feedback}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        # Parse JSON output
        result_json = json.loads(response.choices[0].message.content)
        
        # Handle cases where the model wraps the list in a top-level object
        if isinstance(result_json, dict):
            tickets_data = next(iter(result_json.values()))
        else:
            tickets_data = result_json

        # Convert to Pandas DataFrame
        df = pd.DataFrame(tickets_data)
        
        # Rename columns for clean presentation
        df.columns = [
            "Ticket Summary", 
            "Category", 
            "Sentiment", 
            "Escalation Needed", 
            "Priority", 
            "Suggested Response"
        ]
        
        # Sort by Escalation (Yes first) and Priority
        priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
        if "Priority" in df.columns:
            df["priority_rank"] = df["Priority"].map(priority_order)
            df = df.sort_values(by=["Escalation Needed", "priority_rank"], ascending=[False, True]).drop(columns=["priority_rank"])

        return df, f"Successfully processed {len(df)} tickets."

    except Exception as e:
        return pd.DataFrame(), f"Error processing feedback: {str(e)}"