#!/usr/bin/env python3

import logging
import traceback
import functools
from threading import Thread


def run_threaded(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()

def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("airmonitor.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def catch_exceptions():
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                log = logging.getLogger("AirMonitor")
                log.error(traceback.format_exc())
                
        return wrapper
    return catch_exceptions_decorator
