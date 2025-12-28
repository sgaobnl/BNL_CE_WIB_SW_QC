# # pip install gitpython
import os

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        os.system(f'rmdir /s /q "{folder_path}"')
        print(f"Deleted existing folder: {folder_path}")


def clone_repo(repo_url, branch_name, destination_path):
    delete_folder(destination_path)
    try:
        os.makedirs(destination_path, exist_ok=True)
        os.system(f'git clone --branch {branch_name} --single-branch {repo_url} "{destination_path}"')
        print(f"Branch '{branch_name}' cloned to: {destination_path}")
    except Exception as ex:
        print(f"Error cloning repository: {ex}")

def clear_and_copy_all_to_remote(local_path, remote_user, remote_host, remote_path):
    try:
        clear_command = f'ssh {remote_user}@{remote_host} "rm -rf {remote_path}/* {remote_path}/.* 2>/dev/null"'
        os.system(clear_command)
        print(f"Cleared remote directory: {remote_path}")

        copy_command = f'scp -r "{local_path}/." {remote_user}@{remote_host}:{remote_path}'
        os.system(copy_command)
        print(f"Copied all contents of {local_path} to {remote_user}@{remote_host}:{remote_path}")
    except Exception as ex:
        print(f"Error handling remote files: {ex}")

repo_url = "https://github.com/sgaobnl/BNL_CE_WIB_SW_QC.git"
branch_name = "CTS_FEMB_QC"
local_path = "D:/github/repository"
remote_user = "root"
remote_host = "192.168.121.123"
remote_path = "/home/root/BNL_CE_WIB_SW_QC/"
clone_repo(repo_url, branch_name, local_path)
clear_and_copy_all_to_remote(local_path, remote_user, remote_host, remote_path)
