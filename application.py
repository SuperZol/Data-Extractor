import os
import shutil
import subprocess
import time

import Constants


def delete_folders(zip_dir, xml_dir):
    try:
        print(f"folder path {zip_dir}")
        shutil.rmtree(zip_dir, ignore_errors=True)
        print(f"Deleted folder: {xml_dir}")
        shutil.rmtree(xml_dir, ignore_errors=True)
    except Exception as e:
        print(e)


# Function to run script files by name
def run_script(script_name):
    script_path = os.path.join(os.getcwd(), script_name)
    print(f"script path {script_path}")
    try:
        subprocess.run(["python", script_path], shell=True)
        print(f"Executed script: {script_name}")
    except Exception as e:
        print(f"Failed to execute script: {script_name}\nError: {str(e)}")


if __name__ == "__main__":
    # Delete the specified folder
    script_names = [
        "main.py",
        "xml_extractor.py",
        "data_parser.py"
    ]

    # Schedule the script to run every 24 hours
    while True:
        delete_folders(Constants.ZIP_FILES_DIRECTORY, Constants.XML_FILES_DIRECTORY)
        for script_name in script_names:
            run_script(script_name)
        time.sleep(86400)  # Sleep for 24 hours (24 * 60 * 60 seconds)
