import os
import ctypes
import subprocess
import shutil
import json

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

def run_command(command:list):
    try:
        # 执行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"