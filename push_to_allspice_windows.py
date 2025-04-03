 # -*- coding: utf-8 -*-

import os
import sys
import time
import codecs
import shutil
import pathlib
import requests
import subprocess

################################################################################
VERSION = "1.0.5"

################################################################################
PUSH_TO_ALLSPICE_SCRIPT_URL = "https://raw.githubusercontent.com/polypour/testy/refs/heads/main/push_to_allspice_windows.py"
#PUSH_TO_ALLSPICE_SCRIPT_URL = "https://hub.allspice.io/AllSpice-Demos/Perforce-AllSpice-Integration/raw/branch/main/push_to_allspice_windows.py"
REMOTE_SCRIPT_MODULE_PATH = "C:\allspice\tmp\\"
REMOTE_SCRIPT_TEMP_LOCATION = "C:/allspice/tmp/tmp.py"
LOCAL_SCRIPT_LOCATION = "C:/allspice/push_to_allspice_windows.py"

################################################################################
def remote_script_is_newer_version(v2):
    v1 = VERSION
    if v1 == v2:
        return False

    v1t = [int(num) for num in v1.split('.')]
    v2t = [int(num) for num in v2.split('.')]

    for v1v, v2v in zip(v1t, v2t):
        if v1v > v2v:
            return False
        elif v2v > v1v:
            return True

################################################################################
def download_latest_push_to_allspice_script():
    try:
        response = requests.get(PUSH_TO_ALLSPICE_SCRIPT_URL, stream=True)
        response.raise_for_status()
        with open(REMOTE_SCRIPT_TEMP_LOCATION, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False

################################################################################
def check_and_update_self():
    # Try to download the latest script version from source
    download_successful = download_latest_push_to_allspice_script()
    # If remote script successfully downloaded
    if download_successful:
        # Get the script version from the downloaded file
        module_path = REMOTE_SCRIPT_MODULE_PATH
        if module_path not in sys.path:
            sys.path.append(module_path)
        from tmp import VERSION as EXT_VERSION
        # Check if remote version newer than current
        if remote_script_is_newer_version(EXT_VERSION):
            # Update our own script with the newer version
            shutil.copy2(REMOTE_SCRIPT_TEMP_LOCATION, LOCAL_SCRIPT_LOCATION)
            return True
    # If we didn't update
    return False

################################################################################
def add_indent(input_str, num_spaces, leading_char, secondary_char=None):
    primary_char_indent = (' ' * num_spaces) + leading_char + ' '
    if secondary_char:
        secondary_char_indent = (' ' * num_spaces) + secondary_char + ' '
    else:
        secondary_char_indent = primary_char_indent
    return (primary_char_indent + input_str).replace('\n', '\n' + secondary_char_indent)

################################################################################
def find_allspice_config_files_in_depot(depot_root):
    print("- Finding AllSpice project folders...")
    # Initialize a list for storing found allspice.txt paths
    config_file_paths = []
    # Walk the depot tree
    for root, dirs, files in os.walk(depot_root):
        for file_name in files:
            if file_name == "allspice.txt":
                config_file_path = os.path.join(root, file_name)
                print(add_indent(os.path.dirname(config_file_path), 8, '-'))
                config_file_paths.append(config_file_path)
    # Return config file paths found
    return config_file_paths

################################################################################
def initialize_git_repo():
    print(add_indent("Initializing git repository", 8, '-'))
    if os.path.isdir('.git'):
        print(add_indent(".git folder already exists", 15, '>>'))
    else:
        git_init_process = subprocess.run("git init", capture_output=True, text=True, shell=True)
        print(add_indent(git_init_process.stdout.strip(), 15, '>>'))

################################################################################
def add_allspice_remote():
    print(add_indent("Adding AllSpice remote", 8, '-'))
    # Check if remote already exists
    git_remote_list_process = subprocess.run("git remote -v", capture_output=True, text=True, shell=True)

    if (allspice_repo_url in git_remote_list_process.stdout) or (allspice_repo_url in git_remote_list_process.stderr):
        print(add_indent("AllSpice remote already exists", 15, '>>'))
    else:
        git_add_remote_process = subprocess.run("git remote add origin " + allspice_repo_url, capture_output=True, text=True, shell=True)

################################################################################
def fetch_from_allspice():
    print(add_indent("Fetching from AllSpice remote", 8, '-'))
    git_fetch_process = subprocess.run("git fetch", capture_output=True, text=True, shell=True)
    if git_fetch_process.stdout.strip() or git_fetch_process.stderr.strip():
        print(add_indent(git_fetch_process.stdout.strip(), 15, '>>'))
        print(add_indent(git_fetch_process.stderr.strip(), 15, '>>'))
    else:
        print(add_indent("Nothing new...", 15, '>>'))

################################################################################
def checkout_develop_branch():
    print(add_indent("Checking out develop branch", 8, '-'))
    git_checkout_develop_process = subprocess.run("git checkout develop", capture_output=True, text=True, shell=True)
    print(add_indent(git_checkout_develop_process.stdout.strip(), 15, '>>'))
    print(add_indent(git_checkout_develop_process.stderr.strip(), 15, '>>'))

################################################################################
def show_git_status():
    print(add_indent("Git status:", 8, '-'))
    git_status_process = subprocess.run("git status", capture_output=True, text=True, shell=True)
    if "Untracked" in git_status_process.stdout.strip():
        print(add_indent(git_status_process.stdout.strip(), 15, '>>'))
        print(add_indent(git_status_process.stderr.strip(), 15, '>>'))
    else:
        print(add_indent(git_status_process.stdout.strip(), 15, '>>'))

################################################################################
def get_list_of_modified_files():
    print(add_indent("Modified files found:", 8, '-'))
    git_modified_files_process = subprocess.run("git ls-files --modified", capture_output=True, text=True, shell=True)
    git_modified_files_output = git_modified_files_process.stdout.strip()
    modified_files = git_modified_files_output.split('\n') if git_modified_files_output else []
    if modified_files:
        for cur_file in modified_files:
            print(add_indent(str(cur_file), 15, '>>'))
    else:
        print(add_indent("None", 15, '>>'))
    return modified_files

################################################################################
def get_list_of_untracked_files():
    print(add_indent("Untracked files found:", 8, '-'))
    git_untracked_files_process = subprocess.run("git ls-files --others --exclude-standard", capture_output=True, text=True, shell=True)
    git_untracked_files_output = git_untracked_files_process.stdout.strip()
    untracked_files = git_untracked_files_output.split('\n') if git_untracked_files_output else []
    if untracked_files:
        for cur_file in untracked_files:
            print(add_indent(str(cur_file), 15, '>>'))
    else:
        print(add_indent("None", 15, '>>'))
    return untracked_files

################################################################################
def add_modified_or_untracked_files_for_commit():
    git_add_process = subprocess.run("git add .", capture_output=True, text=True, shell=True)
    print(add_indent("Added modified and/or untracked files to stage for commit", 8, '-'))

################################################################################
def prompt_user_for_commit_message():
    print("")
    print(add_indent("Please enter your commit message for project " + proj_dir + ":", 8, '-'))
    commit_message = input()
    print("")
    return commit_message

################################################################################
def commit_changes(commit_message):
    print(add_indent("Committing with the following message: " + "\"" + commit_message + "\"", 8, '-'))
    git_commit_process = subprocess.run("git commit -m \"" + commit_message + "\"", capture_output=True, text=True, shell=True)
    print(add_indent(git_commit_process.stdout.strip(), 15, '>>'))

################################################################################
def push_commit_to_allspice():
    print(add_indent("Pushing changes to AllSpice on the develop branch...", 8, '-'))
    git_push_process = subprocess.run("git push", capture_output=True, text=True, shell=True)
    print(add_indent(git_push_process.stdout.strip(), 15, '>>'))
    print(add_indent(git_push_process.stderr.strip(), 15, '>>'))

################################################################################
if __name__ == "__main__":
    print("- Starting Perforce -> AllSpice sync...")
    # Check if a newer version exists and update self
    check_and_update_self()
    # Get the absolute path to depot root
    depot_root_absolute_path = os.path.abspath(".")
    # Find AllSpice config files in the Perforce depot
    allspice_config_paths = find_allspice_config_files_in_depot(".")
    print("\n--------------------------------------------------\n")
    # Process the found config files
    for config_file_path in allspice_config_paths:
        # Get the directory path without the filename
        proj_dir = os.path.dirname(config_file_path)
        print("- Processing project folder " + proj_dir)
        # Read file contents
        with open(config_file_path, 'r') as f:
            allspice_repo_url = f.read().strip()
            print(add_indent("AllSpice URL is " + allspice_repo_url, 8, '-'))
        # Change directory to project directory root
        os.chdir(proj_dir)
        # Initialize a git repository in this folder
        initialize_git_repo()
        # Add the AllSpice remote
        add_allspice_remote()
        # Git fetch
        fetch_from_allspice()
        # Checkout develop branch
        checkout_develop_branch()
        # Show git status
        show_git_status()
        # Get list of modified files
        modified_files = get_list_of_modified_files()
        # Get list of untracked files
        untracked_files = get_list_of_untracked_files()
        # If there are any untracked or modified files, start pushing to AllSpice
        if modified_files or untracked_files:
            # Add files to commit
            add_modified_or_untracked_files_for_commit()
            # Ask user for a commit message
            commit_message = prompt_user_for_commit_message()
            # Prepare a commit with the commit message
            commit_changes(commit_message)
        # Push commit to allspice
        push_commit_to_allspice()
        print(add_indent("Completed processing project folder " + proj_dir, 8, '-'))
        # Change directory back to depot root
        os.chdir("..")
        print("\n--------------------------------------------------\n")
    print("- Perforce->AllSpice sync completed!")
