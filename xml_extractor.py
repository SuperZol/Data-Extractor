import gzip
import os
import shutil

import Constants


def unzip_xml_files(directory, supermarket, file):
    zip_path = os.path.join(directory, file)
    xml_file_name = file.split('.gz')[0] + '.xml'
    xml_folder_path = os.path.join(Constants.XML_FILES_DIRECTORY, supermarket)
    if not os.path.exists(xml_folder_path):
        os.makedirs(xml_folder_path)
    xml_file_path = os.path.join(Constants.XML_FILES_DIRECTORY, supermarket, xml_file_name)
    if zip_path.endswith('xml'):
        shutil.copy(str(zip_path), str(xml_folder_path))
    else:
        with gzip.open(zip_path, 'rb') as f_in, open(xml_file_path, 'wb') as f_out:
            try:
                shutil.copyfileobj(f_in, f_out)
            except gzip.BadGzipFile:
                print("Error: Not a valid Gzip file or file is corrupted.", xml_file_path)
            except FileNotFoundError:
                print("Error: File not found.")
            except Exception as e:
                print("An unexpected error occurred:", e)


def main():
    zip_directory = Constants.ZIP_FILES_DIRECTORY
    for supermarket in os.listdir(zip_directory):
        supermarket_path = os.path.join(zip_directory, supermarket)
        for filename in os.listdir(supermarket_path):
            unzip_xml_files(supermarket_path, supermarket, filename)


if __name__ == '__main__':
    main()
