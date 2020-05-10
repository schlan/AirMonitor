#!/usr/bin/env python3

from datastore import AirMonitorDbClient
from i2c import I2C
from scd30.ref_python_scd30 import SCD30

if __name__ == "__main__":
    db = AirMonitorDbClient('test')

    i2c = I2C(bus=1)

    scd30 = SCD30(i2c, 0x61)
    print(scd30.set_temperature_offset(2.5))
    print(scd30.get_temperature_offset())
    #print(scd30.read_measurement())
    


