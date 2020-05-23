#!/usr/bin/env python3

from influxdb import InfluxDBClient
from datetime import datetime

class AirMonitorDbClient:

    def __init__(self, mode):
        self.client = InfluxDBClient('localhost', 8086, 'python', 'cHzSQ7EWcsmY4q3ctyNB', 'airmonitor')
        self.mode = mode

    def get_mean_value(self, desc, sensor, interval, location='unknown'):
        query = """
            SELECT 
                mean("value")
            FROM 
                "{desc}" 
            WHERE 
                "mode" = $mode 
                AND "sensor" = $sensor 
                AND "location" = $location
                GROUP BY time({interval}) fill(linear)
            ORDER BY DESC 
            LIMIT 5
        """

        if desc == 'temp':
            query = query.format(desc = "temp", interval = '{}s'.format(int(interval)))
        elif desc == 'co2':
            query = query.format(desc = "co2", interval = '{}s'.format(int(interval)))
        elif desc == 'rh':
            query = query.format(desc = "rh", interval = '{}s'.format(int(interval)))
        else:
            raise Exception("no supported")

        result = self.client.query(query, bind_params={
            'desc': desc, 
            'sensor': sensor, 
            'location': location, 
            'mode': self.mode,
            'interval': interval})

        result = list(result.get_points())
        
        for value in result:
            if value['mean']:
                return float(value['mean'])
        
        return 0.0


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
