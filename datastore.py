#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import datetime

class AirMonitorDbClient:

    def __init__(self, mode):
        self.client = InfluxDBClient('localhost', 8086, 'python', 'cHzSQ7EWcsmY4q3ctyNB', 'airmonitor')
        self.mode = mode


    def record_value(self, desc, value, time=None, sensor=None, location='unknown'):
        if time == None:
            time = datetime.utcnow().isoformat() + "Z"

        body = [{
            "measurement": str(desc),
            "tags": {
                "location": str(location),
                "sensor": str(sensor),
                "mode": self.mode,
            },   
            "fields": {
                "value": value
            },
            "time": str(time), 
        }]

        self.client.write_points(body)
