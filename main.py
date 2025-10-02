import os
import sys
current_dir = ''
if hasattr(sys,'_MEIPASS'):
    current_dir = os.path.dirname(sys.argv[0])
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from common import *
import bios_parse
import setup_var
from shutil import get_terminal_size
import boot_set
from global_configs import global_configs as configs
set_auto_boot = True
cur_title = None

#全局变量
global_version = [2,1,0,0]
global_configs = configs

columns, rows = get_terminal_size()
print_c("\n" * rows)

if is_admin():
    print_c("已在管理员权限下运行\n")
else:
    print_c("已在用户权限下运行\n")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    exit(1)

columns, rows = get_terminal_size()
print_c("\n" * rows)
print_c("本程序用于一站完成ru修改uefi变量\n","blue")
print_c("为完成目的需要涉及到修改启动项，此功能可以在程序内关闭，作为代替，请手动在运行后将文件夹下EFI文件夹复制到fat32分区自行引导\n")
print_c(">使用方式：\n","cyan")
print_c("回复菜单序号以进行下一步操作,首先通过搜寻选项找到要改的值（菜单或搜索变量）,随后保存&写入引导生成引导文件\n")
print_c(">自动引导：\n","cyan")
print_c("自动配置引导会在 保存&写入引导 时将脚本修改到主机引导首位,并在重启时启动脚本，脚本运行后自动删除自身引导使系统引导回到首位\n")
print_c(      "！！注意！！\n自动引导需要一个已经挂载的Fat32分区10M左右空间以放置引导，请提前挂载！！\n"
      "！！注意！！\n程序暂未添加检测引导选项，如果使用自动配置引导，请勿多次保存配置，这将会导致添加多个引导选项，请重启配置完后再保存。\n","magenta")
print_c(f"v{global_version[0]}.{global_version[1]}.{global_version[2]}.{global_version[3]}\n")
print_c("MADE BY 不锈钢电热水壶","grey")
os.system("pause")

arg = input("是否跳过BIOS DUMP？(y/n 默认：n）")
if arg == 'y' or arg == 'Y' or arg == 'yes' or arg == 'Yes' or arg == 'YES':
    bios_parse.init(True, False)
else:
    bios_parse.init(False,True)

return_string = ("",None)#记录每次指令的返回提示

def load_config_files(skip_choose = 0):
    setup_var.rm_all_var_setting()
    #选择装载的配置文件（限制2个）
    global return_string
    configs_file_list = setup_var.get_all_config_json_files()
    arg_list = []
    load_info = None
    print_string = ''

    #加载指定配置文件
    state = None
    if skip_choose == 0:
        if configs_file_list:
            try:
                for i,configs_file_name in enumerate(configs_file_list):
                    print_c(f"{i+1}: {configs_file_name}")
                arg_list.append(configs_file_list[int(input("选择装载的配置文件1>"))-1])
                arg_list.append(configs_file_list[int(input("选择装载的配置文件2>"))-1])
                state = 0 #指定文件
            except ValueError:
                print_string = "自动使用上一次的json"
                state = 1
        else:
            print_string = "无配置文件，使用默认json"
            state = 2
    else:
        state = 1


    while True:
        if state == 0:
            #使用自定义方案
            result = global_configs.get_option("loaded_jsons")
            if not result[0]:
                print_string = "无全局配置，新建配置并使用默认json"
                state = 3
                continue
            loaded_files_dicts = result[1]
            if not(loaded_files_dicts[str(0)] == arg_list[0]) and (loaded_files_dicts[str(1)] == arg_list[1]):
                loaded_files_dicts[str(len(loaded_files_dicts))] = arg_list
            global_configs.set_option("loaded_jsons_recent", arg_list).save_to_file()
            break
        elif state == 1:
            # 使用上一次方案
            result = global_configs.get_option("loaded_jsons_recent")
            arg_list = result[1]
            break
        elif state == 2:
            # 使用空白方案
            arg_list = []
            global_configs.set_option("loaded_jsons/0", arg_list).set_option("loaded_jsons_recent", arg_list).save_to_file()
            break
        elif state == 3:
            # 新建全局文件
            global_configs.set_option("loaded_jsons", {}).set_option("loaded_jsons_recent", []).save_to_file()
            state = 0
            continue

    load_info = setup_var.load_json(arg_list)
    if not load_info[0]:
        if not load_info[1] == "NoFile":
            for i in load_info[1]:
                print_string += f"报存选项{i}读取失败，已跳过读取"
    else:
        print_string += f"读取完成"

    return_string = (print_string,"cyan")

load_config_files(0)

while True:
    # 打印新页面
    columns, rows = get_terminal_size()
    print_c("\n" * rows)

    if setup_var.add_options_list_final_code:
        print_c("修改缓存列表：")
        j = 0
        for i in setup_var.add_options_list:
            j +=1
            print_c(f"{j}: {i[0]} ---> {setup_var.add_oneOf_display_cache[j-1]}")
        print_c("\n")
    if cur_title is not None:
        print_c(f"当前指定菜单：{cur_title[1]}\n")

    print("\n")
    print_c(*iter(return_string))

    tmp_str = ""
    tmp_str2 = ""
    if set_auto_boot:
        tmp_str = "关闭"
        tmp_str2 = "3. 写入引导并重启"
    else:
        tmp_str = "开启"
        tmp_str2 = "3. 保存为EFI文件夹并关闭（只保存脚本文件夹 .EFI)"


    arg = input(f"1. 通过变量名称查找选项\n2. 通过菜单名称查找选项\n{tmp_str2}\n4. {tmp_str}自动引导\n5. 删除暂存项目\n6. 删除已有方案\n7. 重载已有方案\n8. 新建json方案\n9. 重新选择json>")
    if arg == '1':
        try:
            name = input("名称：>")
            result = setup_var.search_offset_name(name)
            if not result:
                return_string = ("没有此项","red")
                continue
            setup_var.print_offset_list(result)
            which = input("哪一个：>")


            if (which is None) or(which == "") or int(which) > len(result) or int(which) <= 0:
                return_string = ("无效选择","red")
                continue

            setup_var.print_loaded_json_files()
            which_json = input("写入哪个json文件：>")

            if (result[int(which) - 1][1]) == "OneOf":
                setup_var.print_oneOf_option_detail(setup_var.search_oneOf_offset_options_detail(result[int(which)-1][2]))

            value = input("改多少：>")
            if (value == "") or not setup_var.add_var_setting(result[int(which)-1], int(value),int(which_json)-1) :
                return_string = ("无效选择","red")
                continue
            setup_var.refresh_json()
        except Exception as e:
            return_string = (e, "red")
            continue



    elif arg == '2':
        try:
            re_choose = False
            if cur_title is not None:
                result = setup_var.search_offset_name_by_title_index(cur_title[2])
                setup_var.print_offset_list(result)
                print_c("0:重新寻找一个列表...")

                which = input("哪一个：>")
                if (which is None) or(which == "") or int(which) > len(result) or int(which) < 0:
                    return_string = ("无效选择","red")
                    continue

                setup_var.print_loaded_json_files()
                which_json = input("写入哪个json文件：>")

                if (result[int(which) - 1][1]) == "OneOf":
                    setup_var.print_oneOf_option_detail(setup_var.search_oneOf_offset_options_detail(result[int(which) - 1][2]))
                if int(which) == 0:
                    re_choose = True
                else:
                    value = input("改多少:>")
                    if (value == "") or not setup_var.add_var_setting(result[int(which) - 1], int(value),int(which_json)-1):
                        return_string = ("值不符合要求","red")
                        continue
            setup_var.refresh_json()
        except Exception as e:
            return_string = (e, "red")
            continue

        if (cur_title is None) or re_choose:
            t_name = input("菜单名：>")
            result = setup_var.search_offset_title(t_name)
            if result:
                setup_var.print_title_list(result)
            else:
                return_string = ("没有搜到...今日无事可做...","red")
                continue


            title = input("第几个：>")
            if (title == "") or int(title) > len(result) or int(title) < 0:
                return_string = ("数目不符合要求","red")
                continue

            cur_title = result[int(title)-1]


    elif arg == '3':
        try:
            if not setup_var.add_options_list_final_code:
                return_string = ("没有缓存的选项可保存...今日无事可做...","red")
                continue
            if set_auto_boot:
                result = boot_set.save_and_set_boot()
                if not result[0]:
                    if result[1] == "nodisk":
                        return_string = ("没有找到合适的引导设备，请先挂载一个fat32/efi分区","red")
                        continue
                    else:
                        return_string = (result[1],"red")
                        continue
            else:
                boot_set.save_and_only_create_boot_dir()
                print_c("即将重启计算机......", "red")
                os.system("pause")
                os.system("shutdown /r /t 0")
                exit(0)

        except Exception as e:
            return_string = (e, "red")
            continue


    elif arg == '4':
        if set_auto_boot:
            set_auto_boot = False
        else:
            set_auto_boot = True

    elif arg == '5':
        try:
            if not setup_var.add_options_list_final_code:
                return_string = ("没有缓存的选项...今日无事可做...","red")
                continue
            which = input("哪一个(可使用半角逗号间隔):>")
            input_list = which.split(",")
            if input_list is None or len(input_list) == 0:
                return_string = ("无效选择","red")
                continue

            # 转换字符串到数字
            index_list = []
            cache_len = len(setup_var.add_options_list_final_code)
            is_error = False
            for i in input_list:
                try:
                    if (i == "") or int(i) > cache_len or int(i) <= 0:
                        return_string = ("无效选择","red")
                        is_error = True
                        break
                except ValueError as e:
                    return_string = ("无效的字符","red")
                    is_error = True
                    break
                index_list.append(int(i))
            if is_error:
                continue

            index_list.sort()
            for i,elem in enumerate(index_list):
                setup_var.rm_var_setting(elem-i-1)
                setup_var.refresh_json()
        except Exception as e:
            return_string = (e, "red")
            continue

    elif arg == '6':
        try:
            jsons_dict:dict = global_configs.get_option('loaded_jsons')[1]

            for i, json_file_i in enumerate(jsons_dict.keys()):
                print_string_ = ''
                if not jsons_dict[json_file_i]:
                    print_string_ = "default.json"
                else:
                    for elem in jsons_dict[json_file_i]:
                        print_string_ += os.path.basename(elem)
                        print_string_ += "  "
                print_c(f"{i + 1}:{print_string_}", "background")

            which = input("删除哪个>")
            jsons_dict.pop(str(int(which)-1))

            tmp_dict = {}
            for i,elem in enumerate(jsons_dict.values()):
                tmp_dict[str(i)] = elem
            global_configs.set_option('loaded_jsons',tmp_dict).save_to_file()

        except Exception as e:
            return_string = (e, "red")
            continue

    elif arg == '7':
        jsons_dict: dict = global_configs.get_option('loaded_jsons')[1]

        try:
            for i, json_file_i in enumerate(jsons_dict.keys()):
                print_string_ = ''
                if not jsons_dict[json_file_i]:
                    print_string_ = "default.json"
                else:
                    for elem in jsons_dict[json_file_i]:
                        print_string_ += os.path.basename(elem)
                        print_string_ += "  "
                print_c(f"{i + 1}:{print_string_}", "background")

            which = input("加载哪个>")
            global_configs.set_option('loaded_jsons_recent', jsons_dict[str(int(which)-1)]).save_to_file()
            load_config_files(1)
        except Exception as e:
            return_string = (e, "red")
            continue

    elif arg == '8':
        name = input("新建名称>")
        setup_var.create_json(name)

    elif arg == '9':
        load_config_files(0)

    else:
        return_string = ("无法识别的指令...","red")
        continue

    return_string = ("成功","cyan")
