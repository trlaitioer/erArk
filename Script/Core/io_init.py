# -*- coding: UTF-8 -*-
import threading
import queue
import json
from Script.Core import main_frame
from Script.Config import game_config, normal_config

input_evnet = threading.Event()
_send_queue = queue.Queue()
_order_queue = queue.Queue()
order_swap = None


def _input_evnet_set(order):
    """
    推送一个命令
    Keyword arguments:
    order -- 命令
    """
    put_order(order)


def get_order():
    """
    获取一个命令
    """
    return _order_queue.get()


main_frame.bind_return(_input_evnet_set)
main_frame.bind_queue(_send_queue)


def _get_input_event():
    """
    获取输入事件锁
    """
    return input_evnet


def run(open_func: object):
    """
    运行游戏
    Keyword arguments:
    open_func -- 开场流程函数
    """
    global _flowthread
    _flowthread = threading.Thread(target=open_func, name="flowthread")
    _flowthread.start()
    main_frame.run()


def put_queue(message: object):
    """
    向输出队列中推送信息
    Keyword arguments:
    message -- 推送的信息
    """
    _send_queue.put_nowait(message)


def put_order(message: str):
    """
    向命令队列中推送信息
    Keyword arguments:
    message -- 推送的信息
    """
    _order_queue.put_nowait(message)


# #######################################################################
# json 构建函数


def new_json():
    """
    定义一个通用json结构
    """
    flow_json = {}
    flow_json["content"] = []
    return flow_json


def normalize_style_type(style: tuple | str) -> list:
    if isinstance(style, str):
        return [style]
    else:
        return list(style)


def text_json(string: str, style: tuple or str):
    """
    定义一个文本json
    Keyword arguments:
    string -- 要显示的文本
    style -- 显示时的样式
    """
    re = {}
    re["type"] = "text"
    re["text"] = string
    re["style"] = normalize_style_type(style)
    return re


def cmd_json(
    cmd_str: str,
    cmd_num: int,
    normal_style: tuple or str,
    on_style: tuple or str,
):
    """
    定义一个命令json
    Keyword arguments:
    cmd_str -- 命令文本
    cmd_num -- 命令数字
    normal_style -- 正常显示样式
    on_style -- 鼠标在其上时显示样式
    """
    re = {}
    re["type"] = "cmd"
    re["text"] = cmd_str
    re["num"] = cmd_num
    re["normal_style"] = normalize_style_type(normal_style)
    re["on_style"] = normalize_style_type(on_style)
    return re


def style_json(
    style_name: str,
    foreground: str,
    background: str,
    font: str,
    fontsize: str,
    bold: str,
    underline: str,
    italic: str,
):
    """
    定义一个样式json
    Keyword arguments:
    style_name -- 样式名称
    foreground -- 前景色/字体颜色
    background -- 背景色
    font -- 字体
    fontsize -- 字号
    bold -- 加粗
    underline -- 下划线
    italic -- 斜体
    """
    re = {}
    re["style_name"] = style_name
    re["foreground"] = foreground
    re["background"] = background
    re["font"] = font
    re["fontsize"] = fontsize
    re["bold"] = bold
    re["underline"] = underline
    re["italic"] = italic
    return re


# #######################################################################
# 输出格式化


def era_print(string: str, style="standard"):
    """
    输出命令
    Keyword arguments:
    string -- 输出文本
    style -- 显示样式
    """
    json_str = new_json()
    json_str["content"].append(text_json(string, style))
    put_queue(json_str)


def image_print(image_name: str):
    """
    图片输出命令
    Keyword arguments:
    image_name -- 图片名称
    image_path -- 图片路径
    """
    json_str = new_json()
    image_json = {"image_name": image_name}
    json_str["image"] = image_json
    put_queue(json_str)


def clear_screen():
    """
    清屏
    """
    json_str = new_json()
    json_str["clear_cmd"] = "true"
    put_queue(json_str)


def frame_style_def(
    style_name: str,
    foreground: str,
    background: str,
    font: str,
    fontsize: str,
    bold: str,
    underline: str,
    italic: str,
):
    """
    推送一条在前端定义样式的信息
    Keyword arguments:
    style_name -- 样式名称
    foreground -- 前景色/字体颜色
    background -- 背景色
    font -- 字体
    fontsize -- 字号
    bold -- 加粗， 用1表示使用
    underline -- 下划线，用1表示使用
    italic -- 斜体，用1表示使用
    """
    json_str = new_json()
    json_str["set_style"] = style_json(
        style_name,
        foreground,
        background,
        font,
        fontsize,
        bold,
        underline,
        italic,
    )
    put_queue(json_str)


def set_background(color: str):
    """
    设置前端背景颜色
    Keyword arguments:
    color -- 颜色
    """
    json_str = new_json()
    json_str["bgcolor"] = color
    put_queue(json_str)


def clear_order():
    """
    清除前端已经设置的命令
    """
    json_str = new_json()
    json_str["clearorder_cmd"] = "true"
    put_queue(json_str)


def io_print_cmd(cmd_str: str, cmd_number: int, normal_style="standard", on_style="onbutton"):
    """
    打印一条指令
    Keyword arguments:
    cmd_str -- 命令文本
    cmd_number -- 命令数字
    normal_style -- 正常显示样式
    on_style -- 鼠标在其上时显示样式
    """
    json_str = new_json()
    json_str["content"].append(cmd_json(cmd_str, cmd_number, normal_style, on_style))
    put_queue(json_str)


def io_print_image_cmd(cmd_str: str, cmd_number: int):
    """
    打印图片指令
    Keyword arguments:
    cmd_str -- 命令文本
    cmd_number -- 命令数字
    """
    json_str = new_json()
    data = {}
    data["type"] = "image_cmd"
    data["text"] = cmd_str
    data["num"] = cmd_number
    json_str["content"].append(data)
    put_queue(json_str)


def io_clear_cmd(*cmd_numbers: int):
    """
    清除命令
    Keyword arguments:
    cmd_number -- 命令数字，不输入则清楚当前已有的全部命令
    """
    json_str = new_json()
    if cmd_numbers:
        json_str["clearcmd_cmd"] = cmd_numbers
    else:
        json_str["clearcmd_cmd"] = "all"
    put_queue(json_str)


def style_def():
    pass


def init_style():
    """
    富文本样式初始化
    """
    global style_def

    def new_style_def(
        style_name,
        foreground,
        background,
        font,
        fontsize,
        bold,
        underline,
        italic,
    ):
        frame_style_def(
            style_name,
            foreground,
            background,
            font,
            fontsize,
            bold,
            underline,
            italic,
        )

    style_def = new_style_def
    style_list = game_config.config_font
    standard_data = style_list[0]
    for style_id in style_list:
        style = style_list[style_id]
        for k in standard_data.__dict__:
            if k not in style.__dict__:
                style.__dict__[k] = standard_data.__dict__[k]
        if "font" not in style.__dict__ or style.font == "":
            style.font = normal_config.config_normal.font
        style_def(
            style.name,
            style.foreground,
            style.background,
            style.font,
            normal_config.config_normal.font_size,
            style.bold,
            style.underline,
            style.italic,
        )
