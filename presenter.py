#!/usr/bin/env python3

from display import Display
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
import requests
from IT8951 import DisplayModes

BLACK = 0
RED = 76

class Presenter:

    def __init__(self, db):
        self.db = db
        self.font24 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 20)
        self.font56 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 56)
        self.font52 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 52)
        self.mono13 = ImageFont.truetype('./fonts/FiraCode-SemiBold.ttf', 13)

    def render(self, disp, width, height, refresh_interval):
        image = disp.frame_buf

        temp_img = self.paint_box(200, 100, "Temperature", self.db.get_mean_value("temp", "bme280", refresh_interval), "°C")
        image.paste(temp_img, (0, 0))
        disp.draw_partial(DisplayModes.GC16)

        co2_img = self.paint_box(200, 100, "CO2", self.db.get_mean_value("co2", "scd30", refresh_interval), "ppm")
        image.paste(co2_img, (200, 0))
        disp.draw_partial(DisplayModes.GC16)

        rh_img = self.paint_box(200, 100, "Relative Humidity", self.db.get_mean_value("rh", "scd30", refresh_interval), "%")
        image.paste(rh_img, (400, 0))
        disp.draw_partial(DisplayModes.GC16)

        pressure_img = self.paint_box(200, 100, "Pressure", self.db.get_mean_value("pressure", "bme280", refresh_interval), "hPa")
        image.paste(pressure_img, (600, 0))
        disp.draw_partial(DisplayModes.GC16)
        
        pm25_img = self.paint_box(200, 100, "PM 2.5", self.db.get_mean_value("pm25", "sds011", refresh_interval), "μg/m³")
        image.paste(pm25_img, (600, 100))
        disp.draw_partial(DisplayModes.GC16)
        
        pm10_img = self.paint_box(200, 100, "PM 10", self.db.get_mean_value("pm10", "sds011", refresh_interval), "μg/m³")
        image.paste(pm10_img, (600, 200))
        disp.draw_partial(DisplayModes.GC16)
    
        date = self.date()
        image.paste(date, (width - date.width, height - date.height))
        disp.draw_partial(DisplayModes.GC16)
        
        weather = self.weather(width, 100)
        image.paste(weather, (0, height - 100 - date.height - 5))
        disp.draw_partial(DisplayModes.GC16)

        return image

    def paint_box(self, w, h, title, value, unit):
        (image, draw) = self.image(w, h)
        
        # Center title
        title = "{} ({})".format(title, unit)
        x = self.center(w, title, self.font24)
        draw.text((x, 5), title, font = self.font24, fill = RED)

        # Draw value
        value_string = '{:.2f}'.format(value)
        x = self.center(w, value_string, self.font56)
        draw.text((x, 32), value_string, font = self.font52, fill = BLACK)
        
        return image

    def weather(self, width, height):
        weather = requests.get("https://wttr.in/?Tn1FQ").text.splitlines()

        now = weather[:5]
        forecast = weather[9:-1]

        result = []
        for n, f in zip(now, forecast):
            t_line = n.ljust(30, ' ')
            f_line = f[:-1].replace('│', ' ')
            result.append("{}  {}".format(t_line, f_line))
        forecast = "\n".join(result)
        
        (image, draw) = self.image(width, height)
        draw.text((self.center(width, result[0], self.mono13), 0), forecast, font = self.mono13, fill = 0)
        return image

    def date(self):
        date = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
        (x, y, w, h) = self.font24.getmask(date).getbbox()

        (image, draw) = self.image(w, h)
        draw.text((0, 0), date, font = self.font24, fill = BLACK)
        return image

    def center(self, parent_width, text, font):
        (x, y, w, h) = font.getmask(text).getbbox()
        return int((parent_width / 2) - (w + x) / 2)

    def image(self, width, height):
        image = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(image)
        return (image, draw)