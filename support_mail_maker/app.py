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
from gettext import npgettext
import os
import sys
from datetime import datetime
from types import NoneType
from typing import Union, Dict, Any
import json
import gradio as gr
from loguru import logger
from formatter import Formatter
from utils import log_file
from gradio_log import Log
import csv

# Initialize current formatter with the current date
now = datetime.now().strftime("%Y-%m-%d")
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


def on_select(value, evt: gr.EventData):
    current_edition.include_markdown = value
    

def build_interface(formatter):
    """
    Build the Gradio interface for SupportMail Auto Formatter.
    """
    with gr.Blocks() as application:
        create_header()
        inp, inp2 = create_inputs()
        process_btn, markdown_option, output_log = create_actions()
        define_interactivity_logic(inp, inp2)
        download_file = create_output()
        process_btn.click(
            fn=is_ready_to_publish, inputs=[inp, inp2], outputs=download_file
        )
        markdown_option.select(fn=on_select, inputs=markdown_option)
    return application

def create_header():
    """
    Create the header and instructions for the Gradio app.
    """
    with gr.Column():
        gr.Markdown("# SupportMail Auto Formatter")
        gr.Markdown(
            """
            ### Instructions:
            1. Enter JSON Content into the JSON field or Upload it Via the File Upload Field. _Note: These Are Mutually Exclusive. Adding a Value To Both Will Cause an Error._ \n
            2. Press the 'Send To Presses' button to format content into SupportMail Format.\n
            3. Download the formatted file when completed.
        """
        )


def create_inputs():
    """
    Create input fields for JSON content and file upload.
    """
    with gr.Row():
        gr.HTML("<h2>Content Input</h2>")
    with gr.Row():
        inp = gr.Textbox(
            label="JSON Content",
            value=PLACEHOLDER_JSON,
            show_label=True,
            interactive=True,
        )
        inp2 = gr.FileExplorer(
            glob="**", file_count="single", label="Select Path to File"
        )
    return inp, inp2


def create_actions():
    """
    Create the process button and log output display.
    """
    with gr.Row():
        md_option = gr.Checkbox(label="Include Markdown with HTML?")
        process_btn = gr.Button("Send To Presses 🖨️", elem_id="send_to_presses")
    with gr.Row():
        output_log = Log(
            log_file=log_file,
            dark=True,
            label="Formatter Status",
            show_label=True,
            interactive=False,
            every=0.1,
            xterm_log_level="DEBUG",

        )
    return process_btn, md_option, output_log

def create_output():
    with gr.Row():
        output_file = gr.File(label="Download File", visible=False)

    return output_file

def define_interactivity_logic(inp: str, inp2: str):
    """
    Define the interactivity logic between input fields.
    """

    def update_interactivity():
        inp_value = inp.value
        inp2_value = inp2.value
        if inp_value != PLACEHOLDER_JSON:
            update_formatter_and_ui(
                "Value Entered in JSON Input Field. Disabling File Upload Option.",
                inp_value,
            )
            inp2.value = None
        else:
            logger.info("Clearing JSON Input Value from Formatter")

        if inp2_value:
            update_formatter_and_ui(
                "Value Entered in File Upload Field. Disabling JSON Input Option.",
                inp2_value,
            )
            inp.value = None
        else:
            logger.info(
                "Value Cleared in File Upload Field. Enabling JSON Input Option."
            )

    def update_formatter_and_ui(log_message, raw_content_value):
        logger.info(log_message)
        logger.info(f"Setting Raw Data on Formatter to: {raw_content_value}")

    return update_interactivity


def is_ready_to_publish(json_input:str, file_input:str,progress=gr.Progress(track_tqdm=True)) -> None:
    """
    Check if content is ready for publishing and trigger formatting.
    """
    logger.debug(f"{type(json_input)} - {json_input}")
    if json_input and json_input != PLACEHOLDER_JSON:
        file_input = None
        current_edition['context']['publish_date'] = current_edition.publish_date.strftime("%Y-%m-%d")
        content = json_input
    elif file_input is not None:
        # Read file content
        with open(file_input, "r") as f:
            json_input = None
            csv_reader = csv.DictReader(f)
            current_edition['context']['publish_date'] = current_edition.publish_date.strftime("%Y-%m-%d")
            content = list(csv_reader)

    else:
        raise ValueError("No valid input provided!")

    # Set content in the formatter and initiate publishing
    try:
        current_edition.set_raw_content(content)
        if current_edition.send_to_press():
            return current_edition.publish()
    except Exception as e:
        raise RuntimeError("Content is not ready for publishing.") from e


@logger.catch
def main(app):
    app.queue().launch()


if __name__ == "__main__":
    UI = build_interface(current_edition)
    try:
        print(
            f"Starting The Presses at http://127.0.0.1:{os.getenv('GRADIO_SERVER_PORT')}...\n\n"
        )
        main(UI)
    except KeyboardInterrupt:
        print("\n\nProgram Terminated By User...")
        sys.exit(0)
