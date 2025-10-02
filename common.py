import os
import ctypes
import subprocess
import shutil
import json
import requests
background_state = True
from tqdm import tqdm

import zipfile

def unzip_file(zip_file_path, extract_to_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_path)



def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def read_json(file_path):
    if not os.path.isfile(file_path) :
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
        return True, None
    except IOError as e:
        return False, e

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_directory_empty(directory):
    # 列出目录中的所有文件和子目录
    items = os.listdir(directory)
    # 判断目录是否为空
    return len(items) == 0

def check_and_create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"文件夹 {directory} 已创建。")
    else:
        print(f"文件夹 {directory} 已经存在。")


def download_file(url, local_filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(local_filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()





def read_file(file_path,type = "rb"):
    try:
        if type == "rb":
            with open(file_path, type) as file:
                return file.read()
        elif type == "r":
            with open(file_path, type,encoding="utf-8") as file:
                return file.read()
    except IOError as e:
        print(f"无法读取文件 {file_path}: {e}")
        return None

def read_file_lines(file_path,type = "rb"):
    if type == "rb":
        with open(file_path, type) as file:
            return file.readlines()
    elif type == "r":
        with open(file_path, type, encoding="utf-8") as file:
            return file.readlines()
    return None

def write_file(file_path,content,type = "wb"):
    if type == "wb":
        with open(file_path, type) as file:
            file.write(content)
    elif type == "a" or type == "w":
        with open(file_path, type,encoding='utf-8') as file:
            file.write(content)


def print_c(string,color:str = "write"):
    if color is None:
        return
    global background_state
    if color == "background":
        if background_state:
            print(f"\033[1;37;100m{string}\033[0m",flush=True)
            background_state = False
            return
        else:
            print(string)
            background_state = True
            return

    if color == "write":
        print(f"{string}")
        return
    if color == "red":
        print(f"\033[1;31m{string}\033[0m")
        return
    if color == "green":
        print(f"\033[1;32m{string}\033[0m")
        return
    if color == "yellow":
        print(f"\033[1;33m{string}\033[0m")
        return
    if color == "blue":
        print(f"\033[1;34m{string}\033[0m")
        return
    if color == "magenta":
        print(f"\033[1;35m{string}\033[0m")
        return
    if color == "cyan":
        print(f"\033[1;36m{string}\033[0m")
        return
    if color == "grey":
        print(f"\033[1;37m{string}\033[0m")
        return
    print(string)

def run_command(command:list):
    try:
        # 执行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"