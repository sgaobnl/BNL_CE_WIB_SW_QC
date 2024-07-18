import os
import time
import subprocess

target_folder = 'E:\FEMB_QC\Tested'

last_scan_file = 'E:\FEMB_QC\Tested\last_scan_results.txt'

def save_last_scan_results(results):
    with open(last_scan_file, 'w') as f:
        for file_path in results:
            f.write(file_path + '\n')

def load_last_scan_results():
    results = set()
    if os.path.exists(last_scan_file):
        with open(last_scan_file, 'r') as f:
            for line in f:
                results.add(line.strip())
    return results

def subrun(command, timeout=30, check=True, exitflg=True, user_input=None):
    global result
    try:
        result = subprocess.run(command,
                                input = user_input,
                                capture_output=True,
                                text=True,
                                timeout=timeout,
                                shell=True,
                                # stdout=subprocess.PIPE,
                                # stderr=subprocess.PIPE,
                                check=check
                                )
    except subprocess.CalledProcessError as e:
        print("Call Error", e.returncode)
        if exitflg:
            print("Call Error FAIL!")
            print("Exit anyway")
            return None
            # exit()
        # continue
    except subprocess.TimeoutExpired as e:
        print("No reponse in %d seconds" % (timeout))
        if exitflg:
            # print (result.stdout)
            print("Timoout FAIL!")
            print("Exit anyway")
            return None
            # exit()
        # continue
    return result

previous_files = load_last_scan_results()

while True:
    current_files = set()
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            current_files.add(os.path.join(root, file))
    # calculate new update document
    new_files = current_files - previous_files
    # update the scan result
    previous_files = current_files

    save_last_scan_results(current_files)

    for file_path in new_files:
        n = []
        print(f'new file detected: {file_path}')
        if '_S0' in file_path:
            n.append(0)
        if '_S1' in file_path:
            n.append(1)
        if '_S2' in file_path:
            n.append(2)
        if '_S3' in file_path:
            n.append(3)

        desired_path = os.path.dirname(file_path)  # get last path
        path = os.path.dirname(desired_path)  # get last path
        path = path.replace('\\', '/')  # get last path
        t_char = file_path[-7:]
        t_num = ''.join([char for char in t_char if char.isdigit()])
        if '_t' in file_path[-9:]:
            time.sleep(10)  # the time is used to copy the whole .bin file
            command = ["python3", "QC_report_all.py", path, "-n"]
            command.extend(map(str, n))  # Convert integers to strings
            command.extend(["-t", t_num])  # Add other arguments
            print(command)
            result = subrun(command, timeout=1000)  # rewrite with Popen later

    time.sleep(5)