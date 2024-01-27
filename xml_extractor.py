import gzip
import os
import shutil

import Constants


def unzip_xml_files(directory, file):
    zip_path = os.path.join(directory, file)
    xml_file_name = file.split('.gz')[0] + '.xml'
    xml_path = os.path.join(Constants.XML_FILES_DIRECTORY, xml_file_name)
    with gzip.open(zip_path, 'rb') as f_in, open(xml_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)


def main():
    zip_directory = Constants.ZIP_FILES_DIRECTORY
    for filename in os.listdir(zip_directory):
        if filename.endswith('.gz'):
            unzip_xml_files(zip_directory, filename)


if __name__ == '__main__':
    main()
