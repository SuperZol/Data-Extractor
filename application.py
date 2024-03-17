import os
import shutil
import subprocess
import time

import Constants


def delete_folder(folder_path):
    try:
        print(f"folder path {folder_path}")
        shutil.rmtree(folder_path, ignore_errors=True)
        print(f"Deleted folder: {folder_path}")
    except Exception as e:
        pass


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
    folder_path = os.path.join(os.getcwd(), Constants.ZIP_FILES_DIRECTORY)
    delete_folder(folder_path)
    script_names = [
        "main.py",
        "xml_extractor.py"
    ]

    for script_name in script_names:
        print(f"script name {script_name}")
        run_script(script_name)

    # Schedule the script to run every 24 hours
    while True:
        time.sleep(86400)  # Sleep for 24 hours (24 * 60 * 60 seconds)
        # Delete the specified folder again and run the scripts
        delete_folder(folder_path)
        for script_name in script_names:
            run_script(script_name)
