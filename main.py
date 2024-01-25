import json
import os

import requests
from lxml import html
from datetime import datetime

from crawler import Crawler_shops
from Osherad import Osherad

file_path = './urls.json'
DIRECTORY_NAME = "zip_files"


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        url_data = data.get('urls', [])  # Get the list of URLs and names
    return url_data


def create_zip_folder():
    # Check if the base directory exists, if not, create it
    if not os.path.exists(DIRECTORY_NAME):
        os.makedirs(DIRECTORY_NAME)


def main():
    url_lst = read_from_file(file_path)
    create_zip_folder()
    for item in url_lst:
        url = item.get('url', '')  # Get the URL from the dictionary
        name = item.get('name', 'Unknown')  # Get the name from the dictionary, default to 'Unknown'
        Crawler_shops(url, DIRECTORY_NAME, name)
    # Osherad(url_lst[1], DIRECTORY_NAME)


if __name__ == '__main__':
    main()
