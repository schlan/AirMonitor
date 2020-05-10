#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import datetime

class AirMonitorDbClient:

    def __init__(self, mode):
        self.client = InfluxDBClient('localhost', 8086, 'python', 'cHzSQ7EWcsmY4q3ctyNB', 'airmonitor')
        self.mode = mode

    def record_value(self, desc, value, time=str(datetime.utcnow().isoformat(timespec='seconds') + "Z"), location='unknown'):

        print(time)
        if self.mode == "test":
            desc = "dev_" + desc

        body = [{
            "measurement": str(desc),
            "tags": {
                "location": str(location),
            },   
            "fields": {
                "value": value
            },
            "time": str(time), 
        }]

        self.client.write_points(body)

       

