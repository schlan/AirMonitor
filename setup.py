#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name='AirMonitor',
    version='1.0',
    description='Monitor the air quality',
    author='Sebastian Chlan',
    author_email='sebastian.chlan@gmail.com',
    url='https://www.example.com/',
    packages=find_packages(),
    install_requires=[
        'influxdb',
        'schedule',
        'serial'
    ]
)
