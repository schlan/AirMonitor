#!/usr/bin/env python3

from pigpio import pi 
import sys

class I2C: 

    def __init__(self, bus, host="127.0.0.1"):
        self.client = pi(host)
        self.bus = bus
        
        if not self.client.connected:
            print("Unable to connect to PIGPIO service")


    def read(self, address, n=1):
        i2c = self.client.i2c_open(self.bus, address)
        try:
            (count, data) = self.client.i2c_read_device(i2c, n)
            if n == count:
                return data
            else:
                print("Did not read enough bytes")
                return False
        except: 
            print("Error reading")
        finally:
            if i2c:
                self.client.i2c_close(i2c)


    def write(self, address, data):
        i2c = self.client.i2c_open(self.bus, address)
        try:
            self.client.i2c_write_device(i2c, data)
        except: 
            print("Error writing")
        finally:
            if i2c:
                self.client.i2c_close(i2c)


    def scan(self):
        addresses = []
        for device in range(128):
            h = self.client.i2c_open(self.bus, device)
            try:
                self.client.i2c_read_byte(h)
                addresses.append(device)
            except:
                pass
            self.client.i2c_close(h)
        return addresses

   
