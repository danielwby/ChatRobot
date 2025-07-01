# -*- coding: utf-8 -*-

import gradio as gr
import mdtex2html
import requests

config_path = 'config/config_qc.txt'
URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
MODEL = "glm-4"
API_KEY = '0f8d7415ed1d476fa2613531258e97e9.yjji8KtRtE8VwQDJ'


def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y


gr.Chatbot.postprocess = postprocess


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


def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text


def predict(input, chatbot, max_length, top_p, temperature, history):
    chatbot.append((parse_text(input), ""))
    for response_msg, history in generate_response(input=input, history=history, max_length=max_length, top_p=top_p,
                                                   temperature=temperature):
        # print(input)
        # print(response_msg)
        # response = response_msg[-1]['content']
        chatbot[-1] = (parse_text(input), parse_text(response_msg))

        yield chatbot, history


# @retry
def generate_response(input, max_length, top_p, temperature, history):
    with open(config_path, "r", encoding='utf-8') as f:
        sys = f.read()
    if history == []:
        history = history + [{"role": "system", "content": sys}]
    text = [{'role': 'user', 'content': input}]
    messages = history + text
    url = URL
    # print(messages)
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }

    data = {
        'model': MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_length,
        'top_p': top_p
    }
    # print(data)
    response = requests.post(url, headers=headers, json=data)
    response_msg = response.json().get('choices')[0].get('message').get('content')
    history = messages + [{"role": 'assistant', 'content': response_msg}]
    print(history)

    yield response_msg, history
    '''for char in response_msg:

        history[-1][1] += char
        #time.sleep(0.05)
        yield history, response_msg'''


def reset_user_input():
    return gr.update(value='')


def reset_state():
    return [], [], None


with gr.Blocks() as demo:
    configs = load_config(config_path)
    origin_temp = 0.8
    origin_top_p = 0.8
    gr.HTML("""<h1 align="center">""" + """测试""" + """</h1>""")

    chatbot = gr.Chatbot()
    with gr.Row():
        with gr.Column(scale=4):
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10)
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("发送", variant="primary")
        with gr.Column(scale=1):
            emptyBtn = gr.Button("清除历史记录")
            max_length = gr.Slider(0, 2048, value=1000, step=1.0, label="Maximum length", interactive=True)
            top_p = gr.Slider(0, 1, value=origin_top_p, step=0.01, label="Top P", interactive=True)
            temperature = gr.Slider(0, 1, value=origin_temp, step=0.01, label="Temperature", interactive=True)

    history = gr.State([])
    submitBtn.click(predict, [user_input, chatbot, max_length, top_p, temperature, history],
                    [chatbot, history], show_progress=True)
    submitBtn.click(reset_user_input, [], [user_input])

    emptyBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)

demo.queue().launch(share=True, inbrowser=True, server_port=6046)
