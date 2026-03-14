# -*- coding: utf-8 -*-
from __future__ import print_function, division
import os
import time
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cv2
# 获取当前脚本所在目录下的 serial.txt 路径
current_dir = Path(__file__).parent
serial_file = current_dir / "serial.txt"

# 读取序列号
try:
    with open(serial_file, "r", encoding="utf-8") as f:
        DEVICE_SERIAL = f.read().strip()
    if not DEVICE_SERIAL:
        raise ValueError("serial.txt 是空的")
except FileNotFoundError:
    print(f"错误：在 {current_dir} 没找到 serial.txt")
    DEVICE_SERIAL = "" # 或者设置一个默认值

VERSION = "1.1.4"
scale = 0.25

template = cv2.imread('./resource/image/character.png')
template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
template_size = template.shape[:2]


def search(img):
    result = cv2.matchTemplate(img, template, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    cv2.rectangle(
        img,
        (min_loc[0], min_loc[1]),
        (min_loc[0] + template_size[1], min_loc[1] + template_size[0]),
        (255, 0, 0),
        4)
    return img, min_loc[0] + template_size[1] / 2, min_loc[1] +  template_size[0]


def pull_screenshot():
    filename = datetime.datetime.now().strftime("%H%M%S") + '.png'
    os.system('mv autojump.png {}'.format(filename))
    #os.system('adb -s 252912bb shell screencap -p /sdcard/Pictures/autojump.png')
    #os.system('adb -s 252912bb pull /sdcard/Pictures/autojump.png ./autojump.png')
    os.system(f'adb -s {DEVICE_SERIAL} shell screencap -p /sdcard/Pictures/autojump.png')
    os.system(f'adb -s {DEVICE_SERIAL} pull /sdcard/Pictures/autojump.png ./autojump.png')


def jump(distance):
    press_time = distance * 1.35
    press_time = int(press_time)
    #cmd = 'adb -s 252912bb shell input swipe 320 410 320 410 ' + str(press_time) #不要硬编码
    cmd = f'adb -s {DEVICE_SERIAL} shell input swipe 320 410 320 410 {press_time}'
    print(cmd)
    os.system(cmd)


def update_data():
    global src_x, src_y

    img = cv2.imread('./autojump.png')
    img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
    img, src_x, src_y = search(img)
    return img


fig = plt.figure()
pull_screenshot()
img = update_data()
im = plt.imshow(img, animated=True)

update = True


def updatefig(*args):
    global update

    if update:
        time.sleep(1)
        pull_screenshot()
        im.set_array(update_data())
        update = False
    return im,


def on_click(event):
    global update    
    global src_x, src_y
    
    dst_x, dst_y = event.xdata, event.ydata

    distance = (dst_x - src_x)**2 + (dst_y - src_y)**2 
    distance = (distance ** 0.5) / scale
    print('distance = ', distance)
    jump(distance)
    update = True


fig.canvas.mpl_connect('button_press_event', on_click)
ani = animation.FuncAnimation(fig, updatefig, interval=5, blit=True)
plt.show()
