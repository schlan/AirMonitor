#!/usr/bin/env python3

from datastore import AirMonitorDbClient
from i2c import I2C
from sensors import SCD30, SDS011, BME280
from time import sleep
from schedule import every, run_pending
from threading import Thread
from datetime import datetime

from display import Display
from PIL import Image,ImageDraw,ImageFont

db = AirMonitorDbClient("test")
i2c = I2C(bus=1)
scd30 = SCD30(i2c, 0x61)
bme280 = BME280(i2c, 0x76)
sds011 = SDS011("/dev/ttyS0")

disp = Display()
font24 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 24)
font56 = ImageFont.truetype('./fonts/Roboto-Medium.ttf', 56)

def init_scd30():
    scd30.start_continous_measurement()
    scd30.set_measurement_interval(10)

def init_sds011():
    sds011.set_report_mode(active=False)
    sds011.sleep(sleep=True)

def load_sds011_data():
    sds011.sleep(sleep=False)

    # Let it warm up
    sleep(30)

    pm25=0
    pm10=0
    # Take 5 readings
    for i in range(5):
        (tmp_pm25, tmp_pm10) = sds011.query()
        pm25 += tmp_pm25
        pm10 += tmp_pm10
        sleep(1)

    pm25/=5
    pm10/=5

    db.record_value("pm25", pm25, sensor="sds011")
    db.record_value("pm10", pm10, sensor="sds011")

    # Turn it off to prolong its life
    sds011.sleep(sleep=True)
    print(f"SDS011: PM25: {pm25}, PM10: {pm10}" )


def load_co2_data():
    while scd30.get_status_ready() != 1:
        sleep(0.2)
    (co2, temp, rh) = scd30.read_measurement()
    db.record_value("co2", co2, sensor="scd30")
    db.record_value("temp", temp, sensor="scd30")
    db.record_value("rh", rh, sensor="scd30")
    print(f"SCD30: CO2: {co2}, Temp: {temp}, Humidity: {rh}" )

def load_bme280_data():
    temp, pressure, h = bme280.read_data()
    db.record_value("temp", temp, sensor="bme280")
    db.record_value("pressure", pressure / 100.0, sensor="bme280")
    print("BME280: Pressure: {:.1f} Temperature: {:.2f}".format(pressure/100.0, temp))

def start_display():
    disp.init()

    while True:
        image1 = Image.new('1', (disp.width, disp.height), 255)
        image2 = Image.new('1', (disp.width, disp.height), 255)
        
        draw1 = ImageDraw.Draw(image1)
        draw2 = ImageDraw.Draw(image2)

        draw2.text((10, 0), 'Temperature', font = font24, fill = 0)
        draw1.text((10, 26), '{:.2f} °C'.format(db.get_value("temp", "bme280")), font = font56, fill = 0)

        draw2.text((250, 0), 'CO2', font = font24, fill = 0)
        draw1.text((250, 26), '{:.2f} ppm'.format(db.get_value("co2", "scd30")), font = font56, fill = 0)

        draw2.text((580, 0), 'Relative Humidity', font = font24, fill = 0)
        draw1.text((580, 26), '{:.2f} %'.format(db.get_value("rh", "scd30")), font = font56, fill = 0)

        date = datetime.now().strftime("%A, %d %B %Y")
        (x, y, w, h) = font24.getmask(date).getbbox()
        draw1.text((disp.width - w - 10, disp.height - h - 5), date, font = font24, fill = 0)

        disp.display(disp.getbuffer(image1), disp.getbuffer(image2))
        sleep(60 * 5)


def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()

if __name__ == "__main__":
    init_scd30()
    init_sds011()
    run_threaded(start_display)

    every(30).seconds.do(run_threaded, load_co2_data)
    every(30).seconds.do(run_threaded, load_bme280_data)
    every(5).minutes.do(run_threaded, load_sds011_data)
    
    while True:
        run_pending()
        sleep(1)

    scd30.stop_continous_measurement()
    sds011.sleep(sleep=True)