import os
import pathlib
import sys
import warnings
import gradio as gr
from loguru import logger


def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")
warnings.filterwarnings(action='ignore', message=r"w+", )

warnings.showwarning = log_warning

with gr.Blocks() as formatter:
    with gr.Column():
        gr.Markdown("# SupportMail Auto Formatter")
        gr.Markdown("""
            ### Instructions:
            1. Select the ticket file from the ZenDesk Tickets API.
            2. Select the comments directory with JSON comments for each ticket.
            """
                    


@logger.catch
def main():
    demo.queue().launch()


if __name__ == "__main__":
    main()