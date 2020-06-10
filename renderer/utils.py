#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, time

BLACK = 0x10 * 0
GRAY_MEDIUM = 0x10 * 8
GRAY_LIGHT = 0x10 * 10

def font_mono(size):
    return ImageFont.truetype('./fonts/FiraCode-SemiBold.ttf', size)

def font(size):
    return ImageFont.truetype('./fonts/Roboto-Medium.ttf', size)

def image(width, height):
    image = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(image)
    return (image, draw)

def center(parent_width, text, font):
    (x, y, w, h) = font.getmask(text).getbbox()
    return int((parent_width / 2) - (w + x) / 2)