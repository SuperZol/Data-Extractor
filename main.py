import json
import os
import Constants
from crawler import CrawlerShops


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        url_data = data.get('urls', [])  # Get the list of URLs and names
    return url_data


def create_zip_folder():
    if not os.path.exists(Constants.ZIP_FILES_DIRECTORY):
        os.makedirs(Constants.ZIP_FILES_DIRECTORY)


def main():
    url_lst = read_from_file(Constants.URL_FILES)
    create_zip_folder()
    for item in url_lst:
        url = item.get(Constants.URL)
        name = item.get(Constants.NAME)
        CrawlerShops(url, name)


if __name__ == '__main__':
    main()
