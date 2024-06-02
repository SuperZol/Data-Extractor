import json
import constants
from crawler import YenotBitan, Victory


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        url_data = data.get('urls', [])  # Get the list of URLs and names
    return url_data


def main():
    url_lst = read_from_file(constants.URL_FILES)
    for item in url_lst:
        url = item.get(constants.URL)
        name = item.get(constants.NAME)
        if "Yenot_bitan" in name:
            YenotBitan(url, name)
        elif "Victory" in name:
            Victory(url, name)


if __name__ == '__main__':
    main()
