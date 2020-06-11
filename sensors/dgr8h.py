#!/usr/bin/env python3

import logging
import time
from RPi import GPIO

STATE_UNKNOWN = -1
STATE_PULSE_START = 1
STATE_PULSE_END = 2


class DGR8H:

    def __init__(self, gpio):
        self.gpio = gpio
        self.rx_last_timestamp = 0
        self.rx_state = STATE_UNKNOWN
        self.rx_bit_count = 0
        self.rx_bits = 0
        self.frames = []
        
    def init(self, callback):
        self.callback = callback
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)
        GPIO.add_event_detect(self.gpio, GPIO.BOTH)
        GPIO.add_event_callback(self.gpio, self.rx_callback)

    def rx_callback(self, gpio):
        timestamp = int(time.perf_counter() * 1000000)
        duration = timestamp - self.rx_last_timestamp
        self.detect_packet(duration, GPIO.input(gpio))
        self.rx_last_timestamp = timestamp

    def comp_timing(self, duration, length):
        return length - (length * 0.1) < duration and length + (length * 0.1) > duration

    def detect_packet(self, duration, high):
        if self.rx_state == STATE_UNKNOWN:
            if high:
                self.rx_state = STATE_PULSE_START

        elif self.rx_state == STATE_PULSE_START:
            if not high and self.comp_timing(duration, 500):
                self.rx_state = STATE_PULSE_END
            else:
                self.rx_state = STATE_UNKNOWN
        
        elif self.rx_state == STATE_PULSE_END:
            if high:
                self.rx_state = STATE_PULSE_START

                if self.comp_timing(duration, 2000):
                    self.rx_bits |= (1 << (36 - 1 - self.rx_bit_count))
                    self.rx_bit_count = self.rx_bit_count + 1

                elif self.comp_timing(duration, 1000):
                    self.rx_bit_count = self.rx_bit_count + 1
                else:
                    self.rx_bits = 0
                    self.rx_bit_count = 0
            else:
                self.rx_state = STATE_UNKNOWN

        if self.rx_bit_count == 36:
            self.frame_found(self.rx_bits)
            self.rx_bits = 0
            self.rx_bit_count = 0
        
        if self.rx_state == STATE_UNKNOWN:
            self.rx_bits = 0
            self.rx_bit_count = 0

    def frame_found(self, frame):
        if (frame >> 26) & 0x1 == 0 and (frame >> 8) & 0xF == 0xF:
            if frame in self.frames:
                self.decode_frame(frame)
                self.frames = []
            else:
                self.frames.append(frame)
            
    def decode_frame(self, frame):
        sensor_id = frame >> 28
        battery = (frame >> 27) & 0x01
        channel = (frame >> 24) & 0x03
        temp = self.twos_comp((frame >> 12) & 0xFFF, 12) * 0.1
        
        humidity = frame & 0xFF
        self.callback({
            'id': sensor_id,
            'battery': battery,
            'channel': channel,
            'temp': temp,
            'humidity': humidity,
        })

    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0: 
            val = val - (1 << bits)        
        return val    