import os
import time

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import requests
import os
import time
from selenium import webdriver
PATH = "C:/Program Files (x86)/chromedriver.exe"


class Osherad:
    def __init__(self, url, directory_name):
        self.url = url
        self.driver = webdriver.Chrome(service=Service(PATH))
        self.driver.get(self.url)
        self.login()
        time.sleep(5)
        self.directory_path = f'{directory_name}/{Osherad.__name__}'  # save it into Mega folder
        self.create_directory()
        self.start_requests()
        time.sleep(50)


    def create_directory(self):
        # Check if the subdirectory for this class instance exists, if not, create it
        if not os.path.exists(self.directory_path):
            os.makedirs(self.directory_path)

    def login(self):
        username = self.driver.find_element(By.XPATH, "//input[@id='username']")
        password = self.driver.find_element(By.XPATH, "//input[@id='password']")
        username.send_keys("osherad")
        password.send_keys("osherad")
        login_button = self.driver.find_element(By.XPATH, "//button[@id='login-button']")
        login_button.click()

    def start_requests(self):
        selenium_cookies = self.driver.get_cookies()
        print(selenium_cookies)
        requests_session = requests.Session()
        for cookie in selenium_cookies:
            requests_session.cookies.set(cookie['name'], cookie['value'])

        response = requests_session.get("https://url.publishedprices.co.il/file")
        print(response.text)
        if response.ok:
            # Save the response text to a file
            with open("response_content.txt", "w", encoding="utf-8") as file:
                file.write(response.text)
            print("Response content saved to 'response_content.txt'")

        # Now you can use the 'session' object to make requests that require authentication
        if response.ok:
            # Parse the HTML
            tree = html.fromstring(response.content)
            print(tree)
            # Find all <a> elements with href containing ".gz"
            links = tree.xpath("//a[contains(@href, '.gz')]")
            for link in links:
                file_url = link.get('href')
                # Check if the URL is absolute or relative
                self.file_url = self.url + '/' + file_url
                self.download_file()

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
        print(f"Downloaded {file_name}")