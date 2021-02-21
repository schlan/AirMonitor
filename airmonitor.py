#!/usr/bin/env python3

from datastore import AirMonitorDbClient
from i2c import I2C
from sensors import SCD30, SDS011, BME280, DGR8H
from time import sleep
from schedule import every, run_pending
from buttons import Buttons

from IT8951 import Display, DisplayModes
from presenter import Presenter
from utils import *

init_logger()

log = logging.getLogger("AirMonitor")

db = AirMonitorDbClient("test")
i2c = I2C(bus=1)
scd30 = SCD30(i2c, 0x61)
bme280 = BME280(i2c, 0x76)
sds011 = SDS011("/dev/ttyS0")
dgr8h = DGR8H(18)
buttons = Buttons([20, 21])

disp = Display(vcom=-1.64)
presenter = Presenter(db)
refresh_interval = 5 * 60

@catch_exceptions()
def init_scd30():
    scd30.start_continous_measurement()
    scd30.set_measurement_interval(10)

@catch_exceptions()
def init_sds011():
    sds011.set_report_mode(active=False)
    sds011.sleep(sleep=True)

@catch_exceptions()
def init_display():
    disp.clear()
    update_display()

@catch_exceptions()
def dgr8h_updated(data):
    db.record_value("temp", data['temp'], sensor="dgr8h")
    db.record_value("rh", data['humidity'], sensor="dgr8h")
    log.info(f"DGR8H: Temp: {data['temp']}, humidity: {data['humidity']}")

@catch_exceptions()
def init_dgr8h():
    dgr8h.init(dgr8h_updated)

@catch_exceptions()
def load_sds011_data():
    sds011.sleep(sleep=False)

    # Let it warm up
    sleep(15)

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
    log.info(f"SDS011: PM25: {pm25}, PM10: {pm10}" )


@catch_exceptions()
def load_co2_data():
    while scd30.get_status_ready() != 1:
        sleep(0.2)
    (co2, temp, rh) = scd30.read_measurement()
    db.record_value("co2", co2, sensor="scd30")
    db.record_value("temp", temp, sensor="scd30")
    db.record_value("rh", rh, sensor="scd30")
    log.info(f"SCD30: CO2: {co2}, Temp: {temp}, Humidity: {rh}" )

@catch_exceptions()
def load_bme280_data():
    temp, pressure, _ = bme280.read_data()
    db.record_value("temp", temp, sensor="bme280")
    db.record_value("pressure", pressure / 100.0, sensor="bme280")
    log.info("BME280: Pressure: {:.1f} Temperature: {:.2f}".format(pressure/100.0, temp))

@catch_exceptions()
def update_display():
    presenter.render(disp, disp.width, disp.height)
    log.info("Display update finished")

def button_click(gpio):
    print(gpio)

def init_buttons():
    buttons.init(button_click)

if __name__ == "__main__":
    log.info("Start")
    init_buttons()
    init_dgr8h()
    init_scd30()
    init_sds011()
    init_display()

    every(30).seconds.do(run_threaded, load_co2_data)
    every(30).seconds.do(run_threaded, load_bme280_data)
    every(30).seconds.do(run_threaded, load_sds011_data)
    every(60).seconds.do(run_threaded, update_display)
    
    while True:
        run_pending()
        sleep(1)    