#!/usr/bin/env python3

from PIL import Image,ImageDraw,ImageFont
from datetime import datetime, time, date
from io import BytesIO
import requests
from .utils import *
import logging
from pytz import utc

log = logging.getLogger("AirMonitor")
map_cache = {}

def weather():
    image = Image.new('RGBA', (int(256 * 5.5), 256 * 3 - 56), (255,255,255,255))

    rain = rain_map()
    tides = tide_info()

    image.paste(rain, (0,0))
    image.paste(tides, (800,0))

    return image


def rain_map():        
    zoom = 7
    
    url = map_url()
    (rain_url, timestamp) = load_pre_info()

    base_map = Image.new('RGBA', (256 * 3, 256 * 3 - 56), (255,255,255,255))
    pre_map = Image.new('RGBA', (256 * 3, 256 * 3 - 56), (255,255,255,255))
    for i, x in enumerate(range(60, 63)):
        for j, y in enumerate(range(40, 43)):
            pre_img = load_tile(rain_url.format(zoom=zoom, x=x, y=y), cachable=False)
            base_img = load_tile(url.format(zoom=zoom, x=x, y=y), cachable=False)

            base_img.paste(pre_img, (0, 0), pre_img)
            pre_map.paste(pre_img, (pre_img.width * i, pre_img.height * j))       
            base_map.paste(base_img, (pre_img.width * i, pre_img.height * j))       

    pre_map.save("/home/pi/pre.png")
    draw = ImageDraw.Draw(base_map)
    draw.text((10, base_map.height - 50), timestamp, font = font(36), fill = GRAY_DARK)

    return base_map

def load_tile(url, cachable=False):
    if cachable and url in map_cache:
        return map_cache[url].copy()

    result = requests.get(url)
    image = Image.open(BytesIO(result.content)).convert('RGBA')
    
    if cachable:
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


def tide_info():
    tide = load_tide_info()

    found_nearest_ts = False
    now = utc.localize(datetime.utcnow())
    tide_table = []

    def calc_delta(t1, t2):
        hours, remainder = divmod((t1 - t2).seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        delta = ''
        if hours > 0:
            delta += '{}h '.format(int(hours))
        delta += '{}\''.format(int(minutes))
        
        return delta

    for i, t in enumerate(tide):
        time = datetime.strptime(t['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        delta = ''

        if time < now:
            color = GRAY_MEDIUM
            delta = '{} ago'.format(calc_delta(now, time))
        if time > now and not found_nearest_ts:
            color = GRAY_V_DARK
            found_nearest_ts = True
            delta = 'in {}'.format(calc_delta(time, now))    
        else:
            color = GRAY_MEDIUM

        timestamp = time.strftime("%H:%M")
        tide_level = "↑ High" if t['high'] else "↓ Low"
        level = "{}cm".format(t['height_cm'])

        tide_table.append(
            [
                {"value": timestamp, "font": font(36), "fill": color},
                {"value": tide_level, "font": font(36), "fill": color},
                {"value": level, "font": font(36), "fill": color},
                {"value": delta, "font": font(36), "fill": color},
            ]
        )

    return table({"value": "Tides", "font": font(42), "fill": GRAY_DARK}, tide_table)

def load_tide_info():
    data = requests.get("https://tidesnear.me/api/v2/stations/tide/3432").json()
    data = data['next_seven_days']

    tide_data = []
    for x in data:
        if 'tidal_events' in data[x]:
            tide_data.extend(data[x]['tidal_events'])

    now = utc.localize(datetime.utcnow())
    index = None
    for i,x in enumerate(tide_data):
        time = datetime.strptime(x['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        if time > now:
            index = i
            break

    return tide_data[(index - 1):(index + 4)]

