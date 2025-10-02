import json
import os
import sys
from typing import Self

import common
current_dir = ''
if hasattr(sys,'_MEIPASS'):
    current_dir = os.path.dirname(sys.argv[0])
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

global_config_file = os.path.join(current_dir, 'config.json')

class GlobalConfig:
    def __init__(self, _global_config_file):
        #记录文件名
        self.global_config_file = _global_config_file
        if not os.path.isfile(self.global_config_file):
            common.write_json(self.global_config_file, {})
            self.buffer:dict = {}
        else:
            self.buffer = common.read_json(self.global_config_file)

    def set_option(self, option_name:str, option_value) -> Self:
        layers= option_name.split('/')
        tmp_dict = self.buffer
        for i,layer in enumerate(layers):
            tmp_value = tmp_dict.get(layer)
            #赋值
            if i == len(layers)-1:
                tmp_dict[layer] = option_value
                break
            #增加层级
            if tmp_value is None:
                tmp_dict[layer] = {}
                tmp_dict = tmp_dict[layer]
            else:
                tmp_dict = tmp_dict[layer]
        return self

    def get_option(self, option_name:str):
        layers = option_name.split('/')
        tmp_dict = self.buffer
        try:
            for i,layer in enumerate(layers):
                if i == len(layers)-1:
                    return True,tmp_dict[layer]
                else:
                    tmp_dict = tmp_dict[layer]
            return False,None
        except KeyError:
            return False,None


    def save_to_file(self):
        common.write_json(self.global_config_file, self.buffer)

global_configs = GlobalConfig(global_config_file)