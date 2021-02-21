#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, time

BLACK = 0x10 * 0
GRAY_V_DARK = 0x10 * 2
GRAY_DARK = 0x10 * 4
GRAY_MEDIUM = 0x10 * 8
GRAY_LIGHT = 0x10 * 10
GRAY_V_LIGHT = 0x10 * 12

def font_mono(size):
    return ImageFont.truetype('./fonts/FiraCode-SemiBold.ttf', size)

def font(size):
    return ImageFont.truetype('./fonts/SFProDisplay-SemiBold.ttf', size)

def image(width, height):
    image = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(image)
    return (image, draw)

def table(head, data):
    num_cols = len(data[0])
    num_rows = len(data)

    col_widths = [0] * num_cols
    row_height = 0

    for i,row in enumerate(data):
        for j,cell in enumerate(row):
            if cell['value'] == '':
                continue
            (_, _, w, h) = cell['font'].getmask(cell['value']).getbbox()
            col_widths[j] = max(col_widths[j], int(w * 1.35))
            row_height = max(row_height, int(h * 1.6))

    (img, draw) = image(sum(col_widths), int(row_height * num_rows))
    for i,row in enumerate(data):
        x = 0
        for j,cell in enumerate(row):
            draw.text((x, (row_height * i)), cell['value'], font = cell['font'], fill = cell['fill'])
            x += col_widths[j]

    (_, _, w, h) = head['font'].getmask(head['value']).getbbox()
    header_height = int(h * 2)
    
    (img2, draw2) = image(sum(col_widths), int(row_height * num_rows) + header_height)
    img2.paste(img, (0, header_height))
    draw2.text((0, 0), head['value'], font = head['font'], fill = head['fill'])
    
    return img2


def center(parent_width, text, font):
    (x, y, w, h) = font.getmask(text).getbbox()
    return int((parent_width / 2) - (w + x) / 2)
