import json
import os

import requests
from lxml import html
from datetime import datetime

from Mega import Mega
from Osherad import Osherad

file_path = './urls.json'
DIRECTORY_NAME = "zip_files"


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        urls = data['urls']
    url_lst = []
    for url in urls:
        url_lst.append(url)
    return url_lst


def create_zip_folder():
    # Check if the base directory exists, if not, create it
    if not os.path.exists(DIRECTORY_NAME):
        os.makedirs(DIRECTORY_NAME)


def main():
    url_lst = read_from_file(file_path)
    create_zip_folder()
    #Mega(url_lst[0], DIRECTORY_NAME)
    Osherad(url_lst[1], DIRECTORY_NAME)


if __name__ == '__main__':
    main()
