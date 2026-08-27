import pandas as pd
import gradio as gr
from feedback_analyzer import analyze_and_triage_feedback, get_dummy_data

# Function to clear all fields
def reset_app():
    return "", pd.DataFrame(), "🟢 **Status:** System Ready"

# Adaptive Light/Dark Mode CSS using Gradio CSS Variables
custom_css = """
/* Container & Spacing */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Adaptive Typography & Header */
.main-title { 
    font-size: 2.1rem; 
    font-weight: 700; 
    letter-spacing: -0.02em;
    color: var(--body-text-color);
    margin-bottom: 4px; 
}

.sub-title { 
    font-size: 0.98rem; 
    color: var(--body-text-color-subdued);
    margin-bottom: 24px; 
}

/* Custom Status Banner */
.status-banner {
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--background-fill-secondary);
    border: 1px solid var(--border-color-primary);
    font-size: 0.9rem;
    color: var(--body-text-color);
}

/* Table Enhancements */
.table-container {
    border-radius: 8px;
    overflow: hidden;
}
"""

with gr.Blocks(
    title="Customer Feedback Triage", 
    css=custom_css, 
    theme=gr.themes.Soft(
        primary_hue="indigo",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"]
    )
) as demo:
    
    # Adaptive Header
    gr.HTML("""
        <div class="main-title">🎧 Operations Feedback Hub</div>
        <div class="sub-title">AI-powered escalation management and customer review triage</div>
    """)

    with gr.Row(equal_height=False):
        # Left Panel: Inputs & Controls
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Input Feedback Batch")
            
            feedback_input = gr.Textbox(
                label="Customer Tickets / Product Reviews",
                lines=11,
                placeholder="Paste customer messages here (one per line or numbered list)...",
                show_label=False
            )
            
            with gr.Row():
                dummy_btn = gr.Button("🎲 Load Sample Batch", variant="secondary")
                reset_btn = gr.Button("🔄 Reset", variant="stop")
                submit_btn = gr.Button("⚡ Analyze & Triage", variant="primary")
            
            status_output = gr.Markdown("🟢 **Status:** System Ready", elem_classes=["status-banner"])

        # Right Panel: Output Queue
        with gr.Column(scale=2):
            gr.Markdown("### 📊 Prioritized Support Queue")
            
            output_table = gr.Dataframe(
                headers=["Ticket Summary", "Category", "Sentiment", "Escalation Needed", "Priority", "Suggested Response"],
                wrap=True,
                interactive=False,
                row_count=5,
                elem_classes=["table-container"]
            )

    # Footer
    gr.Markdown("---")
    gr.Markdown("💡 *Tip: Tickets requiring escalation or marked as Urgent are automatically sorted to the top.*")

    # Event Handlers
    dummy_btn.click(
        fn=get_dummy_data, 
        outputs=feedback_input
    )
    
    reset_btn.click(
        fn=reset_app,
        inputs=[],
        outputs=[feedback_input, output_table, status_output]
    )
    
    submit_btn.click(
        fn=analyze_and_triage_feedback,
        inputs=[feedback_input],
        outputs=[output_table, status_output]
    )

if __name__ == "__main__":
    demo.launch()