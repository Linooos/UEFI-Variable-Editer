import os,sys
from shutil import get_terminal_size

# pyinstaller路径解析
current_dir = ''
if hasattr(sys,'_MEIPASS'):
    current_dir = os.path.dirname(sys.argv[0])
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
if __name__ == "__main__":sys.path.append(current_dir)

import common
import bios_parse

#uefi选项缓存变量
add_options_list_final_code = [] #最终可执行的uefi代码信息的列表
add_options_list = []  #准备写入的uefi的选项信息列表
add_options_to_which_json_file_index = [] #写入选项于哪个json文件的索引
add_oneOf_display_cache = [] #对应选项值的ui名称
setup_var = "setup_var.efi" #uefi引导执行的程序名称

#json配置解析变量
config_directory = os.path.join(current_dir, 'configs') #json配置保存目录
config_files_list = None
loaded_json_files_list:list = [] #已经加载的json文件列表


def get_offset_setting_code(var_store_name,offset,value,bytes=1):
    if type(offset) is str:
        return f"{var_store_name}:{offset}({bytes})={hex(value)}"
    return f"{var_store_name}:{hex(offset)}({bytes})={hex(value)}"

def search_offset_name(name):
    """
    由名称片段作为索引寻找可用选项
    :param name: 名称字符串，可以为 部分 字符串
    :return: 选项偏移列表
    """
    temp_list = bios_parse.regx_offset_info(bios_parse.uefi_variable_file_content,name)
    return temp_list

def search_offset_title(title):
    """
    返回所有菜单的列表，可供以菜单为索引寻找可用选项
    :param title: 名称字符串，可以为 部分 字符串
    :return: 菜单列表
    """
    templist = bios_parse.search_title(title)
    return templist

def search_offset_name_by_title_index(index):
    """
    通过给定从0开始数出现的第n个列表确定其列表下的所有选项
    :param index: 索引
    :return: 变量偏移列表
    """
    temp_list = bios_parse.regx_offset_info(bios_parse.uefi_variable_file_content,index,"menu")
    return temp_list

def search_oneOf_offset_options_detail(name):
    """
    通过给定名称搜索oneof选项
    :param name:
    :return:
    """
    tmp = bios_parse.regx_offset_info(bios_parse.uefi_variable_file_content,name,type="oneOf")
    return tmp

def get_all_config_json_files()->list:
    """
    获取config_directory变量下目录中所有json文件
    :return: 文件名列表
    """
    common.check_and_create_directory(config_directory)
    tmp_list = []
    for path,dirs,files in os.walk(config_directory):
        for file in files:
            if file.lower().endswith(".json"):
                tmp_list.append(os.path.join(path,file))
    return tmp_list

def load_json(configs_file_names_list:list):
    """
    从json文件中加载已有配置
    :param configs_file_names_list: 包含文件名的列表
    :return: 状态信息
    """
    global add_options_list
    global add_options_list_final_code
    global loaded_json_files_list

    #处理传入参数
    if configs_file_names_list is None:
        configs_file_names_list = []
    if not configs_file_names_list: #如果没指定文件则默认分析 default.json
        configs_file_names_list.append('default.json')

    #缓存读取的文件名
    loaded_json_files_list = configs_file_names_list

    for index,config in enumerate(configs_file_names_list):
        lists = common.read_json(os.path.join(config_directory,config))
        error_key = []

        if not lists:
            return False, "NoFile"
        if lists:
            print(lists)
            for i in lists:
                offset_ = search_offset_name(i[0])
                if not offset_:
                    print("键无效")
                    error_key.append(i[0])
                    continue
                for j,elem in enumerate(offset_):
                    if not (elem[2] == i[0] and elem[0] == i[2]):
                        print(f"名称不正确:{elem[2]}!={i[0]}  {elem[0]} != {i[2]}")
                        if j == len(offset_)-1:
                            error_key.append(i[0])
                        continue
                    print(f"成功匹配:{elem[2]}=={i[0]}  {elem[0]} == {i[2]}")
                    add_var_setting(elem,i[1],index)  # 指定选项写入待写区
                    break
        if error_key:
            return False, error_key
    refresh_json()
    return True, None


def refresh_json():
    """
    将当前缓存中待写入的所有选项同步到对应json文件中
    :return:
    """
    tmp_list = []
    for i in range(len(loaded_json_files_list)):
        tmp_list.append([])

    for i,elem in enumerate(add_options_list):
        tmp_list[add_options_to_which_json_file_index[i]].append(elem)

    for i,elem in enumerate(tmp_list):
        common.write_json(os.path.join(config_directory,loaded_json_files_list[i]),elem)

def create_json(name:str):
    base = (name,'.json')
    _name = ''.join(base)
    common.check_and_create_directory(config_directory)
    common.write_json(os.path.join(config_directory,_name),{})

def add_var_setting(search_list,value,config_list_index):
    """
    将修改的属性加入待写列表
    :param config_list_index:为哪个配置文件写入此参数
    :param search_list: 接收由search_offset_name或search_offset_name_by_title_index函数产生的返回值的子项
    :param value: 要更改的值
    :return:
    """
    name = 2
    menu = 0
    type = 1
    help = 3
    store = 4
    offset = 5
    size = 6
    min = 7
    max = 8
    if value<int(search_list[min],16) or value>int(search_list[max],16):
        return False
    if config_list_index<0 or config_list_index>len(loaded_json_files_list):
        return False
    add_options_list_final_code.append(get_offset_setting_code(bios_parse.get_var_store_name(search_list[store]),search_list[offset],value,int(float(search_list[size])/8)))
    add_options_list.append([search_list[name],value,search_list[menu]]) #选项名，更改值，目录名
    add_options_to_which_json_file_index.append(config_list_index)


    #为oneof选项添加UI可读性的信息，方便读数
    if search_list[type] == "OneOf":
        offset_options = search_oneOf_offset_options_detail(search_list[name])
        for i, elem in enumerate(offset_options):
            value_list = elem[1].split(', ')
            value1 = value_list[0]
            if int(value1) == value:
                add_oneOf_display_cache.append(elem[0])
                break
        else:
            add_oneOf_display_cache.append(str(value))

    else:
        add_oneOf_display_cache.append(str(value))
    return True

def rm_var_setting(index):
    """
    清除选定配置
    :param index: 配置索引
    :return:
    """
    add_options_list_final_code.pop(index)
    add_options_to_which_json_file_index.pop(index)
    add_options_list.pop(index)
    add_oneOf_display_cache.pop(index)

def rm_all_var_setting():
    """
    清除配置
    :return:
    """
    global add_options_list_final_code
    global add_options_to_which_json_file_index
    global add_options_list
    global add_oneOf_display_cache
    add_options_list_final_code=[]
    add_options_to_which_json_file_index=[]
    add_options_list=[]
    add_oneOf_display_cache=[]



#----------------------------------------------------------------

def print_offset_list(offset_list):
    """
    打印变量信息
    :param offset_list:
    :return:
    """
    name = 2
    menu = 0
    type = 1
    help = 3
    store = 4
    offset = 5
    size = 6
    min = 7
    max = 8

    j = 0
    print("\n")

    for i in offset_list:
        j+=1
        common.print_c(f"{j:<4}.名称: {i[name]:<50}菜单: {i[menu]:<40}uefi变量: {bios_parse.get_var_store_name(i[store]):<40}偏移: {i[offset]:<10}最小值: {int(i[min],16):<10}最大值: {int(i[max],16):<10}","background")
    print("\n")

def print_oneOf_option_detail(offset_options):
    """
    打印coneof的备选选项
    :param offset_options:
    :return:
    """
    print("\n")
    blank = ' '
    common.print_c("可能的选项: ","cyan")
    common.print_c("\"{写入值}\" : ---> \"{名称}\"", "magenta")
    print("\n")
    for i,elem in enumerate(offset_options) :
        name = elem[0]
        value_list = elem[1].split(', ')
        value = value_list[0]
        print_string = f"\"{value}\" : ---> \"{name}\""
        if len(value_list)>1:
            type1 = value_list[1]
            type2 = value_list[2]
            print_string += f"  {type1},{type2:<100}"
        else:
            print_string += f"{blank:<100}"
        common.print_c(print_string,"background")
    print("\n")





def print_title_list(offset_list):
    print("\n")
    j = 0
    for i in offset_list:
        j+=1
        common.print_c(f"{j}.{i[1]} #{i[2]:<100}","background")
    print("\n")

def print_loaded_json_files():
    print("\n")
    for i,file in enumerate(loaded_json_files_list):
        common.print_c(f"{i+1}.{file}","background")
    print("\n")



def gen_file_content(enable_final_reboot = True):
    '''
    处理待定列表到可执行指令
    :return:
    '''
    code = ""

    for i in range(len(add_options_list_final_code)-1):
        code+=(setup_var+" "+add_options_list_final_code[i]+"\n")

    if enable_final_reboot:
        code += (setup_var + " -r " + add_options_list_final_code[-1] + "\n")
    else:
        code += (setup_var + " " + add_options_list_final_code[-1] + "\n")

    print(f"{code}")
    return code


if __name__ == "__main__":
    bios_parse.init()
    # # 查找列表 ----> 输出列表内选项
    # print_title_list(search_offset_title("mem"))  #通过字符串搜寻选项菜单
    # print(search_offset_name_by_title_index(46)[3]) #选择给定菜单下的某项选项
    # add_var_setting(search_offset_name_by_title_index(46)[3],1) #指定选项写入待写区
    #
    # # 直接查找选项 ----> 输出选项
    # print_offset_list(search_offset_name("imon offset"))
    # add_var_setting(search_offset_name("imon offset")[1],20000)
    #
    # # 转换后的指令
    # print(gen_file_content())

    # print_oneOf_option_detail(search_oneOf_offset_options_detail("Memory profile"))
    #load_json()
    print(add_options_list_final_code)
    print("------------------------------")
    print(add_options_list)


