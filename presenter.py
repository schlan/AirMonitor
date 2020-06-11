#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, time
import requests
from IT8951 import DisplayModes, Display
from io import BytesIO

import seaborn as sns 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter

from renderer import *

BLACK = 0x10 * 0
GRAY_MEDIUM = 0x10 * 8
GRAY_LIGHT = 0x10 * 10

class Presenter:

    def __init__(self, db):
        self.db = db
        self.chart_index = 0
        self.chart_counter = 5
        self.night_mode = False

    def render(self, disp, width, height, refresh_interval):
        if self.is_time_between(time(6, 0), time(1,0)):
            if self.night_mode:
                disp.frame_buf.paste(0xFF, box=(0, 0, disp.width, disp.height))
                self.night_mode = False

            disp.epd.run()
            self.render_day_mode(disp, width, height, refresh_interval)
            disp.epd.sleep()

        elif not self.night_mode:
            self.night_mode = True
            disp.epd.run()
            self.render_night_mode(disp)
            disp.epd.sleep()

    def render_day_mode(self, disp, width, height, refresh_interval):
        self.update_chart(disp, width, height)
        
        temp_img = paint_box(400, 200, "Temperature", self.db.get_mean_value("temp", "bme280", refresh_interval), "°C")
        co2_img = paint_box(400, 200, "CO2", self.db.get_mean_value("co2", "scd30", refresh_interval), "ppm")
        rh_img = paint_box(400, 200, "Relative Humidity", self.db.get_mean_value("rh", "scd30", refresh_interval), "%")
        pressure_img = paint_box(400, 200, "Pressure", self.db.get_mean_value("pressure", "bme280", refresh_interval), "hPa")

        for i, img in enumerate([temp_img, co2_img, rh_img, pressure_img]):
            x = int((width / 4) * i)
            self.paste_and_update(disp, img, (x, 0))
        
        pm_x = int((width / 4) * 3)
        pm25_img = paint_box(400, 200, "PM 2.5", self.db.get_mean_value("pm25", "sds011", refresh_interval), "μg/m³")
        self.paste_and_update(disp, pm25_img, (pm_x, 200))

        pm10_img = paint_box(400, 200, "PM 10", self.db.get_mean_value("pm10", "sds011", refresh_interval), "μg/m³")
        self.paste_and_update(disp, pm10_img, (pm_x, 400))

        out_temp_img = paint_box(400, 200, "O. Temperature", self.db.get_mean_value("temp", "dgr8h", refresh_interval), "°C")
        self.paste_and_update(disp, out_temp_img, (pm_x, 600))
        
        date = self.date()
        self.paste_and_update(disp, date, (width - date.width - 20, height - date.height - 20))
        
        w = weather(width, 200)
        self.paste_and_update(disp, w, (0, height - w.height - date.height - 20))

    def render_night_mode(self, disp):
        (img, draw) = image(disp.width, disp.height)
        x = center(disp.width, "Good Night!", font(104))
        draw.text((x, 15), "Good Night!", font = font(104), fill = GRAY_MEDIUM)
        self.paste_and_update(disp, img, (0, 0))

    def update_chart(self, disp, width, height):
        if self.chart_counter < 5:
            self.chart_counter = self.chart_counter + 1
            return
        else:
            self.chart_counter = 0

        interval = 5 * 60
        args = [
            (weather_map, ()),
            (chart, (self.db, "Temperature", "temp", "bme280", interval, "°C")),
            (chart, (self.db, "Outside Temperature", "temp", "dgr8h", interval, "°C")),
            (chart, (self.db, "Pressure", "pressure", "bme280", interval, "hPa")),
            (chart, (self.db, "Relative Humidity", "rh", "scd30", interval, "%%")),
            (chart, (self.db, "CO2", "co2", "scd30", interval, "ppm")),
            (chart, (self.db, "PM 2.5", "pm25", "sds011", interval, "μg/m³")),
            (chart, (self.db, "PM 10", "pm10", "sds011", interval, "μg/m³"))
        ]
        
        (fn, arg) = args[self.chart_index]
        
        area_w = int(3 * width / 4)
        area_h = int(height - 250 - 200)
        temp_chart_img = fn(*arg)

        chart_x = int((area_w - temp_chart_img.width) / 2)
        chart_y = int((area_h - temp_chart_img.height) / 2)
        disp.frame_buf.paste(0xFF, box=(0, 200, area_w, area_h + 200))
        self.paste_and_update(disp, temp_chart_img, (chart_x, 200 + chart_y))
        self.chart_index = (self.chart_index + 1) % len(args)

    def date(self):
        date = datetime.now().strftime("%A, %d %B %Y %H:%M")
        (_, _, w, h) = font(36).getmask(date).getbbox()

        (img, draw) = image(w, h)
        draw.text((0, 0), date, font = font(36), fill = GRAY_LIGHT)
        return img

    def paste_and_update(self, disp, image, xy):
        disp.frame_buf.paste(image, xy)
        disp.draw_partial(DisplayModes.GL16)
    
    def is_time_between(self, begin_time, end_time, check_time=None):
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:
            return check_time >= begin_time or check_time <= end_time