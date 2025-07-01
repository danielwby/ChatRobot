# -*- coding: utf-8 -*-

import requests, json
import random
import threading
import json
from retrying import retry

proxies = {'http': 'http://localhost:7890', 'https': 'http://localhost:7890'}
# api_key = 'Bearer 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'

@retry
def get_resp(prompt, system):
    url = 'https://api.openai.com/v1/chat/completions'
    sys = [{"role": "system", "content": system}]
    text = [{'role': 'user', 'content': prompt}]
    messages = sys + text

    headers = {
        'Authorization': 'Bearer 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',
        'Content-Type': 'application/json'
    }

    data = {
        'model': 'ft:gpt-3.5-turbo-0613:chatailover::8pFLVOXt',
        #'model': 'gpt-3.5-turbo-1106',
        'messages': messages,
        'temperature': 0.8,
        'max_tokens': 1000,
        'top_p': 0.8
        }

    response = requests.post(url, proxies=proxies, headers=headers, json=data)
    #print(response.json())
    resp = response.json().get('choices')[0].get('message').get('content')
    return resp   

def test(input_sys, filepath, output):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        txt_list = []
        q = "你：" + line
        print(q)
        txt_list.append(q)
        for i in range(0, 5):
            resp = get_resp(line, input_sys)
            a = "祁煜：" + resp
            print(a)
            txt_list.append(a)
        txt_list.append('\n\n\n')
        with open(output, 'a', encoding='utf-8') as file:
            for line in txt_list:
                file.write(line + '\n')
                
def load_config(file_path):
    config = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print(f"配置文件 '{file_path}' 未找到.")
    except Exception as e:
        print(f"加载配置时发生错误: {e}")
    return config


def main():
    filepath = r'test_question/qiyu_test.txt'
    output_path = r'test_question/qiyu_output.txt'
    config_path = 'config/config.txt'
    # system = input("System：")
    configs = load_config(config_path)
    system = configs["system"]
    test(system, filepath, output_path)
    
  
main()

