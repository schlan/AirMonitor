#!/usr/bin/env python3

from display import Display
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

class Presenter:

    def __init__(self, db):
        self.db = db
        self.font24 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 24)
        self.font56 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 56)
    
    def render(self, width, height, refresh_interval):
        image1 = Image.new('1', (width, height), 255)
        image2 = Image.new('1', (width, height), 255)
        
        draw1 = ImageDraw.Draw(image1)
        draw2 = ImageDraw.Draw(image2)

        (temp_img1, temp_img2) = self.paint_box(240, 100, "Temperature", self.db.get_mean_value("temp", "bme280", refresh_interval), "°C")
        image1.paste(temp_img1, (0, 0))
        image2.paste(temp_img2, (0, 0))

        (co2_img1, co2_img2) = self.paint_box(320, 100, "CO2", self.db.get_mean_value("co2", "scd30", refresh_interval), "ppm")
        image1.paste(co2_img1, (240, 0))
        image2.paste(co2_img2, (240, 0))

        (rh_img1, rh_img2) = self.paint_box(240, 100, "Relative Humidity", self.db.get_mean_value("rh", "scd30", refresh_interval), "%")
        image1.paste(rh_img1, (560, 0))
        image2.paste(rh_img2, (560, 0))

        date = datetime.now().strftime("%A, %d %B %Y")
        (x, y, w, h) = self.font24.getmask(date).getbbox()
        draw1.text((width - w - 10, height - h - 5), date, font = self.font24, fill = 0)

        return (image1, image2)


    def paint_box(self, w, h, title, value, unit):
        image1 = Image.new('1', (w, h), 255)
        image2 = Image.new('1', (w, h), 255)
        draw1 = ImageDraw.Draw(image1)
        draw2 = ImageDraw.Draw(image2)

        # Center title
        (x_title, y_title, w_title, h_title) = self.font24.getmask(title).getbbox()
        draw2.text((w / 2 - (w_title + x_title) / 2, 5), title, font = self.font24, fill = 0)

        # Draw value
        value_string = '{:.2f}\u2009{}'.format(value, unit)
        (x_value, y_value, w_value, h_value) = self.font56.getmask(value_string).getbbox()
        draw1.text((w / 2 - (w_value + x_value) / 2, 32), value_string, font = self.font56, fill = 0)
        
        return (image1, image2)