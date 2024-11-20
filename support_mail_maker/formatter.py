from xml.dom import ValidationErr
from django.shortcuts import render
from django.template.loader import render_to_string
from typing import Union, Dict, Any, List, TextIO
from datetime import datetime
import csv
import pathlib
import json
import os
import gradio as gr
from jsonschema import ValidationError
from utils import valid_JSON_input
from tqdm import tqdm
import enum
from markdownify import markdownify as md

from loguru import logger
import django
from django.conf import settings

settings.configure(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["support_mail_maker/templates"],  # Specify the directory containing your templates
            "APP_DIRS": False,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],  # Add context processors if needed
            },
        },
    ]
)
django.setup()


class ItemType(enum.Enum):
    ISSUE = "Issue"
    WIN = "Win"
    Oops = "Oops"
    News = "News"


class Item:
    """Represents an item with a title, summary, customer, and type.

    This class is used to create an item that contains relevant information such as the title, summary, customer, and type. It ensures that the item type is valid by checking against predefined types.

    Args:
        title (str): The title of the item.
        summary (str): A brief summary of the item.
        customer (str): The name of the customer associated with the item.
        item_type (str): The type of the item, which must be valid.
        ticket_url (str, optional): An optional URL related to the item.

    Raises:
        ValueError: If the provided item_type is not valid.
    """

    def __init__(self, title, summary, customer, item_type, ticket_url=None):
        self.data = {
            "title": title,
            "summary": summary,
            "customer": customer,
            "item_type": self.validate_item_type(item_type),
            "ticket_url": ticket_url,
        }

    @staticmethod
    def validate_item_type(item_type):
        """Validates the item type against predefined types.

        This method checks if the provided item type matches any of the valid item types. If a match is found, it returns the corresponding item type; otherwise, it raises a ValueError.

        Args:
            item_type (str): The item type to validate.

        Returns:
            ItemType: The validated item type.

        Raises:
            ValueError: If the item type is invalid.
        """

        for i_type in ItemType:
            if i_type.value.lower() == item_type.lower():
                return i_type
        raise ValueError(f"Invalid Item Type: {item_type}")

    def __getitem__(self, key):
        """
        Allows access to attributes using dictionary-like indexing.
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """
        Allows setting attributes using dictionary-like indexing.
        """
        if key == "item_type":
            value = self.validate_item_type(value)
        self.data[key] = value

    def __iter__(self):
        """
        Allows iteration over the keys of the internal data dictionary.
        """
        return iter(self.data)

    def __repr__(self):
        """
        Returns a string representation of the item.
        """
        return f"Item({self.data})"
    
    def in_dict_format(self):
        return {
            "title": self.data['title'],
            "summary": self.data['summary'],
            "customer": self.data['customer'],
            "item_type": self.data['item_type'].value,
            "ticket_url": self.data['ticket_url']
        }
class Formatter:
    def __init__(self, publish_date: str):
        self.publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
        self.html: str = ""
        self.markdown:str = " "
        self.include_markdown: bool = False
        self.content_data: Union[str, Dict[str, Any]] = {}
        self.context: Dict[str, Any] = {
            "publish_date": None,
            "content": {"issues": [], "oops": [], "wins": [], "news": []},
        }

    def __getitem__(self, key):
        """
        Allows access to Formatter attributes using dictionary-like indexing.
        """
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        """
        Allows setting Formatter attributes using dictionary-like indexing.
        """
        setattr(self, key, value)

    def __iter__(self):
        """
        Allows iteration over Formatter attributes.
        """
        return iter(vars(self))

    def add_item(self, type: str, item: Item) -> None:
        """Add an item to the specified type in the context.

        This method appends the given item to the list associated with the specified type in the context dictionary. It allows for dynamic addition of items based on their type.

        Args:
            type (str): The type under which the item will be added.
            item (Item): The item to be added to the context.

        Returns:
            None
        """
        self.context['content'][type].append(item.in_dict_format())

    def get_items(self, type, /) -> List[Item]:
        return self.context['content'][type]

    def collate_content(self) -> bool:
        """Organize and categorize content data into specific item types.

        This method processes the content data, creating categorized items based on their type and adding them to the appropriate collections. It provides feedback on the number of items collated and raises an error if an unrecognized item type is encountered.

        Returns:
            bool: True if the content was successfully collated, otherwise raises an error.

        Raises:
            RuntimeError: If an error occurs during the collating process or if an unrecognized item type is encountered.
        """
        try:
            for item in tqdm(self.content_data):
                classed_item = Item(
                    title=item['title'],
                    summary=item['summary '],
                    customer=item['customer'],
                    item_type=item['item_type'],
                    ticket_url=item['url'],
                )
                match classed_item['item_type']:
                    case ItemType.ISSUE:
                        self.add_item("issues", classed_item)
                    case ItemType.WIN:
                        self.add_item("wins", classed_item)
                    case ItemType.Oops:
                        self.add_item("oops", classed_item)
                    case ItemType.News:
                        self.add_item("news", classed_item)
                    case _:
                        raise RuntimeError(
                            f"Error: Unable to collate content due to item {classed_item}"
                        )
            logger.success(
                f"Completed collating content! There are {len(self.get_items('issues'))} issue item(s)",
                f"{len(self.get_items('wins'))} win item(s), "
                f"{len(self.get_items('oops'))} oops item(s), "
                f"{len(self.get_items('news'))} news item(s).",
            )
            return True
        except Exception as e:
            raise RuntimeError(str(e)) from e

    def send_to_press(self) -> bool:
        """Determine if the content is ready for publishing.

        This method checks if a publish date is set in the context and validates the JSON input. It ensures that the necessary conditions are met before content can be published.

        Returns:
            bool: True if the content is ready for publishing, otherwise False.
        """
        try:
            if self.context["publish_date"] is not None and self.collate_content():
                try:
                    valid_JSON_input(self.context)
                    return self.publish()
                except ValidationError as ve:
                    logger.error(str(ve))
                    raise RuntimeError(str(ve)) from ve
        except Exception as e:
            logger.error(str(e))
            raise RuntimeError(f"Unable to Publish: {str(e)}") from e

    def set_raw_content(self, data):
        """Assign raw content data for further processing.

        This method sets the provided data to the content_data attribute, enabling subsequent operations on the content. It captures any errors that occur during the assignment and raises them as a RuntimeError.

        Args:
            data (Any): The raw content data to be assigned.

        Returns:
            None

        Raises:
            RuntimeError: If an error occurs during the assignment of the content data.
        """
        try:
            self.content_data = data
        except Exception as e:
            raise RuntimeError(str(e)) from e

    # def parse_input(self) -> Dict[str, Union[datetime, List[str]]]:
    #     try:
    #         if not isinstance(self.content_data, list):
    #             logger.info(
    #                 "File option selected...Preparing to Open File and Parse to Python Dictonary..."
    #             )
    #             with open(input, "r") as file:
    #                 csv_reader = csv.DictReader(file)
    #                 data = list(csv_reader)
    #                 self.content_data = json.loads(data)

    #                 self.collate_content()
    #         else:
    #             self.collate_content()
    #         return True
    #     except Exception as e:
    #         logger.error(f"Unable to Parse Input: {str(e)}")
    #         return False

    @staticmethod
    def save_to_file(filename: str, content: str, file_ext: str = "html") -> str:
        """Save content to a file and return the file path.

        This method saves the given content to a file with the specified filename and extension,
        and then returns the absolute file path.

        Args:
            filename (str): The name of the file (without extension) to save.
            content (str): The content to write into the file.
            file_ext (str, optional): The file extension. Defaults to 'html'.

        Returns:
            str: The absolute path to the saved file.
        """
        file_path = os.path.join(pathlib.Path.cwd(), f"{filename}.{file_ext}")
        try:
            with open(file_path, "w", encoding="utf-8") as output:
                output.write(content)
            return file_path
        except Exception as e:
            raise RuntimeError(f"Failed to save file: {e}") from e

    def publish(self):
        edition = datetime.strftime(self.publish_date, "%l")
        publish_year = datetime.strftime(self.publish_date, "%Y")
        root_filename = f"{publish_year}_support_mail_{edition}"
        logger.debug(self.context)
        html = render_to_string("support_mail_template.html", self.context)

        markdown = md(html)
        return gr.File(value=[ Formatter.save_to_file(filename=root_filename, content=html),Formatter.save_to_file(filename=root_filename, content=markdown, file_ext="md"
                )], visible=True)
        # return gr.File(value=Formatter.save_to_file(root_filename, html),visible=True)
