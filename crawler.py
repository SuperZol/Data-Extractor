import os
import requests
from lxml import html
from datetime import datetime

import Constants


class Crawler_shops:
    def __init__(self, url, super_name):
        self.url = url  # base url
        self.file_url = ""
        self.directory_path = f'{Constants.DIRECTORY_NAME}/{super_name}'  # save it into Mega folder
        self.create_directory()
        self.url_with_current_date()
        self.start_requests()


    def url_with_current_date(self):
        current_date = datetime.now()
        formatted_date = current_date.strftime(Constants.DATE_FORMAT)
        self.url = self.url + '/' + formatted_date

    def create_directory(self):
        # Check if the subdirectory for this class instance exists, if not, create it
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

    def start_requests(self):
        response = requests.get(self.url)
        if response.ok:
            # Parse the HTML
            tree = html.fromstring(response.content)
            # Find all <a> elements with href containing ".gz"
            links = tree.xpath(Constants.LINKS)
            for link in links:
                file_url = link.get('href')
                # Check if the URL is absolute or relative
                self.file_url = self.url + '/' + file_url
                self.download_file()

        response.close()  # Close connection

    def download_file(self):
        response = requests.get(self.file_url, stream=True)
        # Extracts the file name from the URL. This is done by splitting the URL at each slash and taking the last part,
        # which is typically the file name.
        file_name = self.file_url.split('/')[-1]
        file_path = os.path.join(self.directory_path, file_name)
        with open(file_path, 'wb') as file:
            # Iterates over the response data in chunks. 'chunk_size=8192' means that up to 8192 bytes of data will be
            # read into memory at once. This is a form of buffered reading, which is efficient for large files.
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)


