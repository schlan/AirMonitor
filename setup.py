#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension
from sys import version_info

extensions = [
    Extension(
        "IT8951.spi",
        ["IT8951/spi.c"],
        libraries=['bcm2835'],
    )
]

setup(
    name='AirMonitor',
    version='1.0',
    description='Monitor the air quality',
    author='Sebastian Chlan',
    author_email='sebastian.chlan@gmail.com',
    url='https://github.com/schlan/AirMonitor',
    ext_modules=extensions,
    packages=find_packages(),
    setup_requires=[
        'wheel'
    ],
    install_requires=[
        'influxdb',
        'schedule',
        'pyserial',
        'pigpio',
        'spidev',
        'RPi.GPIO',
        'Pillow',
        'requests',
        'pandas',
        'seaborn'
    ]
)
