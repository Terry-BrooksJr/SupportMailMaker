from django.shortcuts import render
from django.template.loader import render_to_string
from typing import Union, Dict, Any, List
from datetime import datetime
import csv
import json
from utils import valid_JSON_input
from tqdm import tqdm
from enum import Enum, property
from loguru import logger
class ItemType(Enum):
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
            'title': title,
            'summary': summary,
            'customer': customer,
            'item_type': self.validate_item_type(item_type),
            'ticket_url': ticket_url
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
        raise ValueError(f'Invalid Item Type: {item_type}')

    def __getitem__(self, key):
        """
        Allows access to attributes using dictionary-like indexing.
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """
        Allows setting attributes using dictionary-like indexing.
        """
        if key == 'item_type':
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

class Formatter:
    def __init__(self, publish_date: str):
        self.publish_date = datetime.strptime(publish_date, '%Y-%m-%d')
        self.html: str = ''
        self.content_data: Union[str, Dict[str, Any]] = {}
        self.context: Dict[str, Any] = {
            'publish_date': None,
            'content': {
                'issues': [],
                'oops': [],
                'wins': [],
                'news': []
            }
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
    def add_item(self, type, item) -> None:
        self.context[type].append(item)

    def get_items(self, type, /) -> List[Item]:
        return self.context[type]
    
    def collate_content(self) -> bool:
        try:
            for item in tqdm(self.content_data):
                classed_item = Item(
                    title=item.title,
                    customer=item.customer,
                    item_type=item.type,
                    ticket_url=item.url
                )
                match classed_item.item_type:
                    case ItemType.ISSUE:
                        self.add_item('issues',classed_item)
                    case ItemType.WIN:
                        self.add_item('wins',classed_item)
                    case ItemType.Oops:
                        self.add_item('oops',classed_item)
                    case ItemType.News:
                        self.add_item('news',classed_item)
                    case _:
                        raise RuntimeError(f'Error: Unable to collate content due to item {classed_item}')
            logger.success(f"Completed collating content! There are {len(self.get_items('issues'))} issue item(s)",
                        f"{len(self.get_items('wins'))} win item(s), "
                        f"{len(self.get_items('oops'))} oops item(s), "
                        f"{len(self.get_items('news'))} news item(s).")
            return True
        except Exception as e:
            raise RuntimeError(str(e)) from e

    def is_ready_for_publishing(self) -> bool:
        if self.context['publish_date'] is not None:
            return valid_JSON_input(self.context)
        return False
    
    def set_raw_content(self, data):
        try:
            self.content_data = data
        except Exception as e:
            raise RuntimeError(str(e)) from e
        

    def parse_input(self) -> Dict[str, Union[datetime, List[str]]]:
        if not isinstance(self.content_data, dict):
            logger.info('File option selected...Preparing to Open File and Parse to Python Dictonary...')
            with open(input, 'r') as file:
                csv_reader = csv.DictReader(file)
                data = list(csv_reader)
                self.content_data = json.loads(data)
                self.context['publish_date'] = datetime.strftime(self.publish_date, '%Y-%m-%d')
                self.collate_content()
        else:
            self.content_data = json.loads(self.content_data)
            self.context['publish_date'] = datetime.strftime(self.publish_date, '%Y-%m-%d')
            self.collate_content()
        return self.context

    def publish(self):
        return render_to_string('support_mail_template.html', self.context)