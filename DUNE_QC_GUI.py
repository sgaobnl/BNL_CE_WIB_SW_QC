import stat
import time

import paramiko
from getpass import getpass
from datetime import datetime
import subprocess
import os

def copy_remote_folder(sftp_client, remote_folder, local_folder):
    os.makedirs(local_folder, exist_ok = True)
    # print(os.makedirs)
    folder_items = sftp_client.listdir(remote_folder)
    # print(folder_items)
    for item in folder_items:
        # print(item)
        remote_path = remote_folder + '/' + item
        local_path = os.path.join(local_folder, item)

        remote_attr = sftp_client.stat(remote_path)

        if stat.S_ISDIR(remote_attr.st_mode):
            copy_remote_folder(sftp_client, remote_path, local_path)
        else:
            sftp_client.get(remote_path, local_path)
#
DeviceName = '192.168.121.123'
port = 22
username = 'root'
password = 'fpga'

directory_path = '/home/root/BNL_CE_WIB_SW_QC/'
remote_folder = '/home/root/BNL_CE_WIB_SW_QC/CHK/'
local_folder = 'E:/data'

# import the system time
local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
command_time = f'date --set "{local_time}"'

remote_script_initial = f'''
date --set "{local_time}"
cd {directory_path}
python3 wib_initial.py
'''

remote_script_checkout = f'''
cd {directory_path}
python3 FEMB_BIST.py
'''
# python3 WIB_Initial

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh_client.connect(DeviceName, port, username, password)
    print(f'connect to {DeviceName}')

    #00 initial configuration
    print(f'Executing command: {remote_script_initial}')
    stdin, stdout, stderr = ssh_client.exec_command(remote_script_initial)
    print('output: ')
    for line in stdout.readlines():
        print(line.strip())
    print(f'Executing command: {remote_script_initial}')

    #01 assembly configuration
    stdin, stdout, stderr = ssh_client.exec_command(remote_script_checkout)
    time.sleep(1)
    print('output: ')
    for line in stdout.readlines():
        print(line.strip())
    print(f'Executing command: {remote_script_checkout}')

    #02 data copy to serve computer
    sftp_client = ssh_client.open_sftp()
    copy_remote_folder(sftp_client, remote_folder, local_folder)
    print(f'Folder {remote_folder} copies to {local_folder} Successfully')


except paramiko.AuthenticationException:
    print(f'connect fail')

except Exception as e:
    print(f'error')

finally:
    # close ssh link
    sftp_client.close()
    ssh_client.close()