#! -*- coding:utf-8 -*-
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
import random

def get_random_color():
    """生成随机背景颜色"""
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))




def validCode_img(request):
    """生成验证码图片"""
    img = Image.new("RGB",(360,50),color=get_random_color())
    draw = ImageDraw.Draw(img)
    kumo_font = ImageFont.truetype("static/font/kumo.ttf",size=40)
    valid_code_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 70 + 20, 5), random_char, get_random_color(), font=kumo_font)
        # 保存验证码字符串
        valid_code_str += random_char
        # 添加噪点
    width=360
    height=50
    for i in range(8):
        x1=random.randint(0,width)
        x2=random.randint(0,width)
        y1=random.randint(0,height)
        y2=random.randint(0,height)
        draw.line((x1,y1,x2,y2),fill=get_random_color())

    for i in range(10):
        draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
    # 使用会话跟踪技术保存当前验证码值
    request.session["valid_code_str"] = valid_code_str
    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()
    return data