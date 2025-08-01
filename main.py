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
set_auto_boot = True
cur_title = None

global_version = [2,1,0,0]

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
load_info = setup_var.load_json()
if not load_info[0]:
    if not load_info[1] == "NoFile":
        print_string = ''
        for i in load_info[1]:
            print_string += f"报存选项{i}读取失败，已跳过读取"
            return_string = (print_string,"red")
else:
    return_string = ("读取成功","cyan")


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
        tmp_str2 = "3. 写入引导（请勿多次写入，如多次写入请使用文件夹下boot.exe删除多余启动项目)"
    else:
        tmp_str = "开启"
        tmp_str2 = "3. 保存为EFI文件夹（只保存脚本文件夹 .EFI)"


    arg = input(f"1. 通过变量名称查找选项\n2. 通过菜单名称查找选项\n{tmp_str2}\n4. {tmp_str}自动引导\n5. 删除暂存项目\n6. 重启\n>")
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
            if (result[int(which) - 1][1]) == "OneOf":
                setup_var.print_oneOf_option_detail(setup_var.search_oneOf_offset_options_detail(result[int(which)-1][2]))
            value = input("改多少：>")
            if (value == "") or not setup_var.add_var_setting(result[int(which)-1], int(value)):
                return_string = ("无效选择","red")
                continue
        except Exception as e:
            print_c(e,"red")
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
                if (result[int(which) - 1][1]) == "OneOf":
                    setup_var.print_oneOf_option_detail(setup_var.search_oneOf_offset_options_detail(result[int(which) - 1][2]))
                if int(which) == 0:
                    re_choose = True
                else:
                    value = input("改多少:>")
                    if (value == "") or not setup_var.add_var_setting(result[int(which) - 1], int(value)):
                        return_string = ("值不符合要求","red")
                        continue
        except Exception as e:
            print_c(e,"red")
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
        except Exception as e:
            print_c(e,"red")
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
        except Exception as e:
            print_c(e,"red")
            continue

    elif arg == '6':
        try:
            result = input("确定要重启吗？(y/n 默认y)")
            if result == 'n'or result == 'N'or result == 'no'or result == 'NO'or result == 'No':
                return_string = ("今日无事可做...","red")
                continue
            os.system("shutdown /r /t 0")
        except Exception as e:
            print_c(e,"red")
            continue

    else:
        return_string = ("无法识别的指令...","red")
        continue

    return_string = ("成功","cyan")
