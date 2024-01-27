import json
import os

import Constants
from crawler import Crawler_shops


file_path = './urls.json'
DIRECTORY_NAME = "zip_files"


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        url_data = data.get('urls', [])  # Get the list of URLs and names
    return url_data


def create_zip_folder():
    # Check if the base directory exists, if not, create it
    if not os.path.exists(Constants.DIRECTORY_NAME):
        os.makedirs(Constants.DIRECTORY_NAME)


def main():
    url_lst = read_from_file(file_path)
    create_zip_folder()
    for item in url_lst:
        url = item.get(Constants.URL)  # Get the URL from the dictionary
        name = item.get(Constants.NAME)  # Get the name from the dictionary, default to 'Unknown'
        Crawler_shops(url, name)


if __name__ == '__main__':
    main()
