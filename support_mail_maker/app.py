# import os
# import pathlib
# import sys
# import warnings
# import gradio as gr
# from loguru import logger
# from formatter import Formatter
# from datetime import datetime 
# from typing import Union, Dict, Any
# from gradio_log import Log
# from utils import log_file


# now = datetime.now().strftime('%Y-%m-%d')
# current_edition = Formatter(publish_date=now)


# placeholder = """
# {
#     "publish_date": "null",
#     "content": {
#         "issues": [],
#         "oops": [],
#         "wins": [],
#         "news": []
#     }
# }
# """
# with gr.Blocks() as formatter:
#     with gr.Column():
#         gr.Markdown("# SupportMail Auto Formatter")
#         gr.Markdown("""
#             ### Instructions:
#             1. Enter JSON Content into the JSON field or Upload it Via the File Upload Field. _Note: These Are Mutually Exclusive. Adding a Value To Both Will Cause an Error \n
#             2. Press the Send To Presses button to format content into SupportMail Format.\n
#             3. Download File When Completed
#             """)
#     with gr.Row():
#         gr.HTML("<h2>Content Input</h2>")
#     with gr.Row():
#         inp = gr.Textbox(label="JSON Content", value=placeholder, show_label=True, interactive=True)
#         inp2 = gr.FileExplorer(glob="**", file_count="single", label="Select Path to File")
#     with gr.Row():
#         process_btn = gr.Button("Send To Presses 🖨️", elem_id="send_to_presses")
#     with gr.Row():
#         output_log = Log(log_file=log_file, dark=True, label="Formatter Status", show_label=True, interactive=False)


#     def update_interactivity(inp_value, inp2_value):
#         if inp_value != placeholder and inp_value.strip():
            
#             _update_formatter_and_ui(
#                 'Value Entered in JSON Input Field. Disabling File Upload Option',
#                 inp2,
#                 inp_value,
#             )   
#         else: 
#             # inp2.update(interactive=True)\
#             logger.info('Clearing Raw Data On Formatter')
#             current_edition.set_raw_content(None)

#         if inp2_value:
#             _update_formatter_and_ui(
#                 'Value Entered in Filed Upload Field. Disabling JSON Input Option',
#                 inp,
#                 inp2_value,
#             )
#         else:
#             logger.info('Value Cleared in Filed Upload Field. Enabling JSON Input Option')
#             logger.info('Clearing Raw Data On Formatter')
#             # inp.update(interactive=True)


#     # TODO Rename this here and in `update_interactivity`
#     def _update_formatter_and_ui(log_message, unselected_input_method, raw_content_value):
#         logger.info(log_message)
#         # unselected_input_method.update(interactive=False)
#         logger.info(f'Setting Raw Data On Formatter to {raw_content_value} ')
#         current_edition.set_raw_content(raw_content_value)
        
#     def is_ready_to_publish(input:Union[str, Dict[str, Any]], progress=gr.Progress(track_tqdm=True)):
#         if current_edition.is_ready_for_publishing():
#             if   current_edition.parse_input(input=input):
#                 return current_edition.current_edition.publish()
            
#     process_btn.click(fn=is_ready_to_publish, inputs=inp, outputs=output_log)
# @logger.catch
# def main():
#     formatter.queue().launch()


# if __name__ == "__main__":
#     try:
#         print(f"Starting The Presses at http://127.0.0.1:{os.getenv('GRADIO_SERVER_PORT')}...\n\n")
#         main()
#     except KeyboardInterrupt:
#         print("\n\nProgram Terminated By User...")
#         sys.exit(0)
import os
import sys
from datetime import datetime
from typing import Union, Dict, Any

import gradio as gr
from loguru import logger
from formatter import Formatter
from utils import log_file
from gradio_log import Log
# Initialize current formatter with the current date
now = datetime.now().strftime('%Y-%m-%d')
current_edition = Formatter(publish_date=now)

# Placeholder JSON content
PLACEHOLDER_JSON = """
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

def build_interface(formatter):
    """
    Build the Gradio interface for SupportMail Auto Formatter.
    """
    with gr.Blocks() as application:
        create_header()
        inp, inp2 = create_inputs()
        process_btn, output_log = create_actions()
        monitor_change = define_interactivity_logic(inp, inp2, formatter)
        process_btn.click(fn=is_ready_to_publish, inputs=[inp, inp2], outputs=output_log)
        inp.change(fn=validate_input, inputs=(inp,inp2),  outputs=output_log)
        inp.submit(fn=validate_input, inputs=(inp,inp2),  outputs=output_log)
        inp2.change(fn=validate_input, inputs=(inp,inp2),  outputs=output_log)
    return application

def create_header():
    """
    Create the header and instructions for the Gradio app.
    """
    with gr.Column():
        gr.Markdown("# SupportMail Auto Formatter")
        gr.Markdown("""
            ### Instructions:
            1. Enter JSON Content into the JSON field or Upload it Via the File Upload Field. _Note: These Are Mutually Exclusive. Adding a Value To Both Will Cause an Error._ \n
            2. Press the 'Send To Presses' button to format content into SupportMail Format.\n
            3. Download the formatted file when completed.
        """)

def create_inputs():
    """
    Create input fields for JSON content and file upload.
    """
    with gr.Row():
        gr.HTML("<h2>Content Input</h2>")
    with gr.Row():
        inp = gr.Textbox(label="JSON Content", value=PLACEHOLDER_JSON, show_label=True, interactive=True)
        inp2 = gr.FileExplorer(glob="**", file_count="single", label="Select Path to File")
    return inp, inp2

def create_actions():
    """
    Create the process button and log output display.
    """
    with gr.Row():
        process_btn = gr.Button("Send To Presses 🖨️", elem_id="send_to_presses")
    with gr.Row():
        output_log = Log(log_file=log_file, dark=True, label="Formatter Status", show_label=True, interactive=False)
    return process_btn, output_log

def define_interactivity_logic(inp:str, inp2:str, formatter_instance:Formatter):
    """
    Define the interactivity logic between input fields.
    """
    def set_values(value:str, formatter_instance: Formatter):
        if formatter_instance.content_data != value:
            if value is not None:
                formatter_instance.set_raw_content(value)
                

    def update_interactivity():
            inp_value = inp.value
            inp2_value = inp2.value
            if inp_value != PLACEHOLDER_JSON:
                update_formatter_and_ui(
                    'Value Entered in JSON Input Field. Disabling File Upload Option.',
                    inp2,
                    inp_value
                )
                inp2.update(value=None)
            else:
                logger.info('Clearing JSON Input Value from Formatter')
                formatter_instance.set_raw_content(None)

            if inp2_value:
                update_formatter_and_ui(
                    'Value Entered in File Upload Field. Disabling JSON Input Option.',
                    inp,
                    inp2_value
                )
                inp.update(value=None)
            else:
                logger.info('Value Cleared in File Upload Field. Enabling JSON Input Option.')
                formatter_instance.set_raw_content(None)

    def update_formatter_and_ui(log_message, unselected_input, raw_content_value):
        logger.info(log_message)
        logger.info(f'Setting Raw Data on Formatter to: {raw_content_value}')
        set_values(raw_content_value, formatter_instance)
    return update_interactivity

def is_ready_to_publish(json_input, file_input, progress=gr.Progress(track_tqdm=True)):
    """
    Check if content is ready for publishing and trigger formatting.
    """
    if json_input.value and json_input.value != PLACEHOLDER_JSON:
        content = json_input.value
    elif file_input:
        # Read file content
        with open(file_input.value, 'r') as f:
            content = f.read()
    else:
        raise ValueError("No valid input provided!")

    # Set content in the formatter and initiate publishing
    formatter.set_raw_content(content)
    if formatter.is_ready_for_publishing():
        return formatter.publish()
    else:
        raise RuntimeError("Content is not ready for publishing.")
      
def validate_input(input1:gr.Textbox, input2:gr.FileExplorer,  formatter_instance:Formatter):               
    if input1.value is None or input1.value == PLACEHOLDER_JSON and input2.value is not None:
        formatter_instance.set_raw_content(input2.value)
    elif input2.value is None and input1.value is not None or input1.value != PLACEHOLDER_JSON: 
        formatter_instance.set_raw_content(input1.value)
    else:
        raise ValueError(f'Unable to determine valid input method!')

@logger.catch
def main(app):
    app.queue().launch()

if __name__ == "__main__":
    formatter = Formatter(now)
    UI = build_interface(formatter)
    try:
        print(f"Starting The Presses at http://127.0.0.1:{os.getenv('GRADIO_SERVER_PORT')}...\n\n")
        main(UI)
    except KeyboardInterrupt:
        print("\n\nProgram Terminated By User...")
        sys.exit(0)