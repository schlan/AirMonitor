#!/usr/bin/env python3

from datastore import AirMonitorDbClient
from i2c import I2C
from sensors import SCD30, SDS011
from time import sleep
from schedule import every, run_pending
from threading import Thread

db = AirMonitorDbClient("test")
i2c = I2C(bus=1)
scd30 = SCD30(i2c, 0x61)
sds011 = SDS011("/dev/ttyS0")

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
    print(f"Reading done. CO2: {co2}, Temp: {temp}, Humidity: {rh}" )

def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()

if __name__ == "__main__":
    init_scd30()
    init_sds011()

    every(30).seconds.do(run_threaded, load_co2_data)
    every(5).minutes.do(run_threaded, load_sds011_data)
    
    while True:
        run_pending()
        sleep(1)

    scd30.stop_continous_measurement()
    sds011.sleep(sleep=True)