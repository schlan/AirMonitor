#!/usr/bin/env python3

from PIL import Image,ImageDraw,ImageFont
from datetime import datetime, time
from io import BytesIO
import requests
from .utils import *
import logging

log = logging.getLogger("AirMonitor")
map_cache = {}

def weather_map():        
    zoom = 7
    
    url = map_url()
    (rain_url, timestamp) = load_pre_info()

    base_map = Image.new('RGBA', (256 * 3, 256 * 3 - 56), (255,255,255,255))
    for i, x in enumerate(range(60, 63)):
        for j, y in enumerate(range(40, 43)):
            pre_img = load_tile(rain_url.format(zoom=zoom, x=x, y=y))
            base_img = load_tile(url.format(zoom=zoom, x=x, y=y), cachable=True)

            base_img.paste(pre_img, (0, 0), pre_img)
            base_map.paste(base_img, (pre_img.width * i, pre_img.height * j))       

    draw = ImageDraw.Draw(base_map)
    draw.text((10, base_map.height - 50), timestamp, font = font(36), fill = GRAY_DARK)

    return base_map

def load_tile(url, cachable=False):
    if url in map_cache and cachable:
        return map_cache[url]

    result = requests.get(url)
    image = Image.open(BytesIO(result.content)).convert('RGBA')
    map_cache[url] = image
    return image

def map_url(token="pk.eyJ1Ijoic2ViY2hsYW4iLCJhIjoiY2tiNHp3NHRvMGtucTJ6bzZqMWp4NWI5ZyJ9.GoKM2Z-fWqCDDgftOZf6cw"):
    return "https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/256/{{zoom}}/{{x}}/{{y}}?access_token={token}".format(token=token)

def load_pre_info():
    rain = requests.get("https://api.met.ie/api/maps/radar").json()
    timestamp = rain[-1]['mapTime']
    server = rain[-1]['server']
    src = rain[-1]['src']

    ts = str(int(datetime.timestamp(datetime.now())))
    rain_url = "{server}/api/maps/radar/{src}/{{x}}/{{y}}/{{zoom}}/{timestamp}".format(server=server, src=src, timestamp=ts)
    
    return (rain_url, rain[-1]['mapTime'])


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

