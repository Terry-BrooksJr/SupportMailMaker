import os
import pathlib
import sys
import warnings
import gradio as gr
from loguru import logger
from formatter import Formatter
from datetime import datetime 
from typing import Union, Dict, Any
from gradio_log import Log
from utils import log_file
import os
def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")
warnings.filterwarnings(action='ignore', message=r"w+", )

warnings.showwarning = log_warning
now = datetime.now().strftime('%Y-%m-%d')
current_edition = Formatter(publish_date=now)


placeholder = """
{
    "publish_date": "null",
    "content": {
        "issues": [],
        "oops": [],
        "wins": [],
        "news": []
    }
}
"""
with gr.Blocks() as formatter:
    with gr.Column():
        gr.Markdown("# SupportMail Auto Formatter")
        gr.Markdown("""
            ### Instructions:
            1. Enter JSON Content into the JSON field or Upload it Via the File Upload Field. _Note: These Are Mutually Exclusive. Adding a Value To Both Will Cause an Error \n
            2. Press the Send To Presses button to format content into SupportMail Format.\n
            3. Download File When Completed
            """)
    with gr.Row():
        gr.HTML("<h2>Content Input</h2>")
    with gr.Row():
        inp = gr.Textbox(label="JSON Content", value=placeholder, show_label=True, show_indices=True)
        inp2 = gr.FileExplorer(glob="*/**.json", file_count="single", label="Select Path to File")
    with gr.Row():
        process_btn = gr.Button("Send To Presses 🖨️", elem_id="send_to_presses")
    with gr.Row():
        Log(log_file=log_file, dark=True, label="Formatter Status", show_label=True)


    def update_interactivity(inp_value, inp2_value):
        if inp_value != placeholder and inp_value.strip():
            _update_formatter_and_ui(
                'Value Entered in JSON Input Field. Disabling File Upload Option',
                inp2,
                inp_value,
            )   
        else:
            logger.info('Value Cleared in JSON Input Field. Enabling File Upload Option')
            inp2.update(interactive=True)
            logger.info('Clearing Raw Data On Formatter')
            current_edition.set_raw_content(None)

        if inp2_value:
            _update_formatter_and_ui(
                'Value Entered in Filed Upload Field. Disabling JSON Input Option',
                inp,
                inp2_value,
            )
        else:
            logger.info('Value Cleared in Filed Upload Field. Enabling JSON Input Option')
            logger.info('Clearing Raw Data On Formatter')
            inp.update(interactive=True)


    # TODO Rename this here and in `update_interactivity`
    def _update_formatter_and_ui(log_message, unselected_input_method, raw_content_value):
        logger.info(log_message)
        unselected_input_method.update(interactive=False)
        logger.info(f'Setting Raw Data On Formatter to {raw_content_value} ')
        current_edition.set_raw_content(raw_content_value)
        
    def is_ready_to_format(input:Union[str, Dict[str, Any]], progress= ):
        if current_edition.is_ready_for_publishing():
            current_edition.parse_input(input=input)


@logger.catch
def main():
    formatter.queue().launch()


if __name__ == "__main__":
    try:
        print(f'Starting The Presses at http://127.0.0.1:{os.getenv('GRADIO_SERVER_PORT')}...\n\n')
        main()
    except KeyboardInterrupt:
        print("\n\nProgram Terminated By User...")
        sys.exit(0)