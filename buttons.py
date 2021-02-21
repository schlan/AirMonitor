#!/usr/bin/env python3

from pigpio import pi, INPUT, FALLING_EDGE, PUD_OFF

class Buttons: 

    def __init__(self, pins, host="127.0.0.1"):
        self.client = pi(host)
        self.pins = pins
        self.callbacks = []

        if not self.client.connected:
            print("Unable to connect to PIGPIO service")

    def init(self, callback):
        self.callback = callback

        for pin in self.pins:
            self.client.set_mode(pin, INPUT)
            self.client.set_pull_up_down(17, PUD_OFF)
            self.client.set_glitch_filter(pin, 250)
            self.callbacks.append(self.client.callback(pin, FALLING_EDGE, self.on_click))

    def on_click(self, gpio, level, tick):
        self.callback(gpio)