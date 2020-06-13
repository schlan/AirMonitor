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
        self.chart_index = 2
        self.chart_counter = 5
        self.night_mode = False

    def render(self, disp, width, height):
        if self.is_time_between(time(6, 0), time(1,0)):
            if self.night_mode:
                disp.frame_buf.paste(0xFF, box=(0, 0, disp.width, disp.height))
                self.night_mode = False

            disp.epd.run()
            self.render_day_mode(disp, width, height)
            disp.epd.sleep()

        elif not self.night_mode:
            self.night_mode = True
            disp.epd.run()
            self.render_night_mode(disp)
            disp.epd.sleep()

    def render_day_mode(self, disp, width, height):
        self.update_chart(disp, width, height)
        self.paint_values(disp, width, height)
        self.date(disp, width, height)
        
    def render_night_mode(self, disp):
        (img, draw) = image(disp.width, disp.height)
        x = center(disp.width, "Good Night!", font(104))
        draw.text((x, 15), "Good Night!", font = font(104), fill = GRAY_MEDIUM)
        self.paste_and_update(disp, img, (0, 0))

    def paint_values(self, disp, width, height):
        interval = 10 * 60
        h = 180
        w = int(width / 4)

        temp_img = paint_box(w, h, "Indoor", self.db.get_mean_value("temp", "bme280", interval), "°C")
        rh_img = paint_box(w, h, "Indoor Humidity", self.db.get_mean_value("rh", "scd30", interval), "%")
        co2_img = paint_box(w, h, "CO2", self.db.get_mean_value("co2", "scd30", interval), "ppm")
        pressure_img = paint_box(w, h, "Pressure", self.db.get_mean_value("pressure", "bme280", interval), "hPa")

        for i, img in enumerate([temp_img, rh_img, co2_img, pressure_img]):
            x = int((width / 4) * i)
            self.paste_and_update(disp, img, (x, 20))

        interval = 15 * 60
        out_temp_img = paint_box(w, h, "Outdoor", self.db.get_mean_value("temp", "dgr8h", interval), "°C")
        out_rh_img = paint_box(w, h, "Outdoor Humidity", self.db.get_mean_value("rh", "dgr8h", interval), "%")
        pm25_img = paint_box(w, h, "PM 2.5", self.db.get_mean_value("pm25", "sds011", interval), "μg/m³")
        pm10_img = paint_box(w, h, "PM 10", self.db.get_mean_value("pm10", "sds011", interval), "μg/m³")

        for i, img in enumerate([out_temp_img, out_rh_img, pm25_img, pm10_img]):
            x = int((width / 4) * i)
            self.paste_and_update(disp, img, (x, 200))

    def update_chart(self, disp, width, height):
        if self.chart_counter < 3:
            self.chart_counter += 1
            return
        else:
            self.chart_counter = 0

        interval = 15 * 60
        args = [
            (
                chart_new,
                (
                    self.db,
                    [
                        ("Indoor Temperatur", "temp", "dgr8h", interval, "°C"),
                        ("Indoor Humidity", "rh", "scd30", interval, "%%"),
                        ("Outdoor Temperatur", "temp", "bme280", interval, "°C"),
                        ("Outdoor Humidity", "rh", "dgr8h", interval, "%%")
                    ]
                ) 
            ),
            (
                chart_new,
                (
                    self.db,
                    [
                        ("CO2", "co2", "scd30", interval, "ppm"),
                        ("Pressure", "pressure", "bme280", interval, "hPa"),
                        ("Particles - PM 2.5", "pm25", "sds011", interval, "μg/m³"),
                        ("Particles - PM 10", "pm10", "sds011", interval, "μg/m³")
                    ]
                ) 
            ),
            (
                weather_map,
                ()
            )
        ]

        (fn, arg) = args[self.chart_index]
        temp_chart_img = fn(*arg)
        

        area_w = width
        area_h = int(height - 400 - 50)
        
        chart_x = int((area_w - temp_chart_img.width) / 2)
        chart_y = int((area_h - temp_chart_img.height) / 2)

        (img, draw) = image(area_w, area_h)
        draw.rectangle([0, 0, area_w, area_h], fill=0xFF, outline=None, width=25)
        disp.frame_buf.paste(img, (0, 400))        

        self.paste_and_update(disp, temp_chart_img, (chart_x, 400 + chart_y))
        self.chart_index = (self.chart_index + 1) % len(args)

    def date(self, disp, width, height):
        date = datetime.now().strftime("%A, %d %B %Y %H:%M")
        (_, _, w, h) = font(42).getmask(date).getbbox()

        (img, draw) = image(w, h)
        draw.text((0, 0), date, font = font(42), fill = GRAY_LIGHT)
        self.paste_and_update(disp, img, (width - img.width - 20, height - img.height - 20))
        

    def paste_and_update(self, disp, image, xy):
        disp.frame_buf.paste(image, xy)
        disp.draw_partial(DisplayModes.GL16)
    
    def is_time_between(self, begin_time, end_time, check_time=None):
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else:
            return check_time >= begin_time or check_time <= end_time