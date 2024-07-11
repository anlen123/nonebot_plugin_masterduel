from PIL import Image
import requests
from io import BytesIO
import base64
import os


def pin_quality(card_id:int, quality:str):
    # 加载URL图片
    url_image_url = f'https://cdn.233.momobako.com/ygopro/pics/{card_id}.jpg'

    # 加载URL图片
    response = requests.get(url_image_url)
    url_image = Image.open(BytesIO(response.content))

    # 加载本地图片
    current_directory = "."
    if not quality:
        return url_image_url

    local_image_path = f'{current_directory}/plugins/nonebot_plugin_masterduel/nonebot_plugin_masterduel/img/{quality}'
    local_image = Image.open(local_image_path).convert('RGBA')
    local_image.thumbnail((local_image.width * 0.5, local_image.height * 0.5))

    # 计算拼接后的图像大小
    result_width = url_image.width
    result_height = url_image.height + local_image.height

    # 创建空白图像作为拼接结果
    result_image = Image.new('RGBA', (result_width, result_height))

    # 将URL图片粘贴到拼接结果的底部
    result_image.paste(url_image, (0, local_image.height))

    # 将本地图片粘贴到拼接结果的顶部
    result_image.paste(local_image, (url_image.width - local_image.width, 0))

    # 粘贴小蓝
    xiaoLan_path = f'{current_directory}/plugins/nonebot_plugin_masterduel/nonebot_plugin_masterduel/img/xiaolan'
    xiaoLan_image = Image.open(xiaoLan_path).convert('RGBA')
    xiaoLan_image.thumbnail((xiaoLan_image.width * 0.36, xiaoLan_image.height * 0.36))
    result_image.paste(xiaoLan_image, (0, 0),xiaoLan_image)

    # 将拼接后的图像转换为Base64格式
    buffered = BytesIO()
    result_image.save(buffered, format='PNG')

    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    return "base64://" + image_base64