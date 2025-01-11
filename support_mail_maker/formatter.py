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
import aiofiles
from loguru import logger
import django
from django.conf import settings

settings.configure(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.environ['SUPPORTMAIL_HTML_TEMPLATE']],  # Template directory
            "APP_DIRS": False,  # Optimization: Set to False if not using app-level templates
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
                # Optimization: Use cached template loader if available
                'loaders': [
                    ('django.template.loaders.cached.Loader', [
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ]),
                ],
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
    """Formatter class for managing and publishing support mail content.

    This class handles content collation, formatting, and publishing, providing methods for adding items, setting content data, and generating output files.
    """
    def __init__(self, publish_date: str):
        self.publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
        self.html: str = ""
        self.markdown:str = ""
        self.content_data: Union[str, Dict[str, Any]] = {}
        self.context: Dict[str, Any] = {
            "publish_date": self.publish_date.strftime('%m/%d/%Y'),
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

    def get_items(self, type:str, /) -> List[Item]:
        return self.context['content'][type]

    async def collate_content(self) -> bool:
        """Organize and categorize content data into specific item types.

        This method processes the content data, creating categorized items based on their type and adding them to the appropriate collections. It provides feedback on the number of items collated and raises an error if an unrecognized item type is encountered.

        Returns:
            bool: True if the content was successfully collated, otherwise raises an error.

        Raises:
            None
        """
        try:
            for item in tqdm(self.content_data):
                if item['include'] == "✅":
                    classed_item = Item(
                        title=item['title'],
                        summary=item['summary'],
                        customer=item['customer'],
                        item_type=item['type'],
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
                            logger.error(
                                f"Error: Unable to collate content due to item {classed_item}"
                            )
            logger.success(f"Completed collating content out of the {len(self.content_data)} items submitted, there are {len(self.get_items('issues'))} issue item(s)")
            logger.success(f"{len(self.get_items('wins'))} win item(s)")
            logger.success(f"{len(self.get_items('oops'))} oops item(s)")
            logger.success(f"{len(self.get_items('news'))} news item(s)")
            return True
        except Exception as e:
            logger.error(f'Unable to Collate content: {str(e)}')

    async def send_to_press_async(self) -> bool:
        """Determine if the content is ready for publishing.

        This method checks if a publish date is set in the context and validates the JSON input. It ensures that the necessary conditions are met before content can be published.

        Returns:
            bool: True if the content is ready for publishing, otherwise False.
        """
        try:
            # 1) Check if a publish date is set
            if self.context["publish_date"] is not None:
                # 2) Properly await collate_content()
                collate_ok = await self.collate_content()
                if collate_ok:
                    try:
                        # 3) Validate the context JSON
                        valid_JSON_input(self.context)
                        # 4) Instead of self.publish(), use your async publish_async
                        await self.publish_async()
                        return True
                    except ValidationError as ve:
                        logger.error(f"Unable to Publish Due to Validation Failure: {str(ve)}")
                        return False
            return False
        except Exception as e:
            logger.error(f"Unable to Publish due to General Press Error: {str(e)}")
            return False

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
            logger.error(f"Unable to Set Raw Content {str(e)}")

    @staticmethod
    async def save_to_file(filename: str, content: str, file_ext: str = "html") -> str:
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
            async with aiofiles.open(file_path, "w", encoding="utf-8") as output:
                await output.write(content)
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

    async def publish_async(self):
        """Publishes the support mail content.

        This method renders the support mail content using the provided context,
        converts it to Markdown, and returns it as a downloadable file.

            Args:
                self (Formatter): The Formatter instance.

            Returns:
                list: A list containing the generated HTML and Markdown files.

        """
        try:
            edition = self.publish_date.strftime("%l")  
            publish_year = self.publish_date.strftime("%Y") 
            root_filename = f"{publish_year}_support_mail_{edition}"

            # Render content (assuming render_to_string is async)
            html = render_to_string("support_mail_template.html", self.context)
            
            # Convert to Markdown (assuming md is async—though often md() is sync)
            markdown =  md(html)
            
            # 1) Await saving of files
            html_path = await self.save_to_file(filename=root_filename, content=html)
            markdown_path = await self.save_to_file(filename=root_filename, content=markdown, file_ext="md")

            logger.success("HTML & Markdown Files Generated. Please Download them below ⬇️")

            # 2) Return Gradio components referencing the saved files
            return [
                gr.File(value=[html_path, markdown_path], visible=True),
                gr.File(visible=False),
                gr.Textbox(visible=False)
            ]

        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            return [
                gr.File(visible=False),
                gr.File(visible=False),
                gr.Textbox(
                    value="Invalid Content File Uploaded. Resetting Press..."
                )]