#!/usr/bin/env python3

from PIL import Image,ImageDraw,ImageFont
from datetime import datetime, time
from io import BytesIO
import requests
from .utils import *

def weather_map():        
    zoom = 7
    
    url = "https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/256/{zoom}/{x}/{y}?access_token=pk.eyJ1Ijoic2ViY2hsYW4iLCJhIjoiY2tiNHp3NHRvMGtucTJ6bzZqMWp4NWI5ZyJ9.GoKM2Z-fWqCDDgftOZf6cw"
    rain = requests.get("https://api.met.ie/api/maps/radar").json()
    
    now = int(datetime.timestamp(datetime.now()))
    rain_url = "{server}/api/maps/radar/{src}/{x}/{y}/{zoom}/{now}"
    src = rain[-1]['src']
    timestamp = rain[-1]['mapTime']
    server = rain[-1]['server']

    base_map = Image.new('RGBA', (256 * 3, 256 * 3 - 56), (255,255,255,255))
    pre_base = Image.new('RGBA', (256 * 3, 256 * 3 - 56), (255,255,255,255))
    for i, x in enumerate(range(60, 63)):
        for j, y in enumerate(range(40, 43)):
            tile = requests.get(rain_url.format(server=server, zoom=zoom, x=x, y=y, src=src, now=now))
            pre_img = Image.open(BytesIO(tile.content)).convert('RGBA')
            
            response = requests.get(url.format(zoom=zoom, x=x, y=y))
            base_img = Image.open(BytesIO(response.content)).convert('RGBA')

            base_img.paste(pre_img, (0,0), pre_img)

            pre_base.paste(pre_img, (pre_img.width * i, pre_img.height * j))        
            base_map.paste(base_img, (pre_img.width * i, pre_img.height * j))       

    draw = ImageDraw.Draw(base_map)
    draw.text((10, 10), timestamp, font = font(36), fill = BLACK)

    return base_map


def weather(width, height):
    weather = requests.get("https://wttr.in/?Tn1FQ").text.splitlines()

    now = weather[:5]
    forecast = weather[9:-1]

    result = []
    for n, f in zip(now, forecast):
        t_line = n.ljust(30, ' ')
        f_line = f[:-1].replace('│', ' ')
        result.append("{}  {}".format(t_line, f_line))
    forecast = "\n".join(result)
    
    (img, draw) = image(width, height)
    draw.text((center(width, result[0], font_mono(32)), 0), forecast, font = font_mono(32), fill = 0)
    return img

