#!/usr/bin/env python3

from datastore import AirMonitorDbClient
from i2c import I2C
from sensors import SCD30
from time import sleep
from schedule import every, run_pending


db = AirMonitorDbClient('test')
i2c = I2C(bus=1)
scd30 = SCD30(i2c, 0x61)

def init_scd30():
    scd.start_continous_measurement()
    

def load_co2_data():
    scd30 = SCD30(i2c, 0x61)
    while scd30.get_status_ready() != 1:
        sleep(0.2)
    (co2, temp, rh) = scd30.read_measurement()
    db.record_value("scd30_co2", co2)
    db.record_value("scd30_temp", temp)
    db.record_value("scd30_rh", rh)
    print(f"Reading done. CO2: {co2}, Temp: {temp}, Humidity: {rh}" )


if __name__ == "__main__":
    every(30).seconds.do(load_co2_data)
    
    while True:
        run_pending()
        sleep(0.1)

    scd.stop_continous_measurement()