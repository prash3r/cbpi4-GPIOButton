
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *

from unittest.mock import MagicMock, patch
import requests

logger = logging.getLogger(__name__)

headers = {
  "Content-Type": "application/json",
  "Accept": "application/json"
}

try:
    import RPi.GPIO as GPIO
except Exception:
    logger.warning("Failed to load RPi.GPIO. Using Mock instead")
    MockRPi = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO

@parameters([Property.Text(label="base_url", configurable=True, default_value="http://127.0.0.1:8000/api", description="enter the base url where your craftbeerpi4 web instance is reachable (without trailing slash)"),
             Property.Number(label="debounce_time", configurable=True, default_value=100, description="debounce time in milli seconds to prevent accidental double triggers"),
             Property.Select(label="gpio_pin", options=["disabled",0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], description="Select the GPIO pin your button is wired to"),
             Property.Select(label="method", options=["GET","POST"], description="GET or POST call to API"),
             Property.Text(label="command_string", configurable=True, default_value="/step/next", description="API command path beginning with slash")])
class GPIOButtonSensor(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(GPIOButtonSensor, self).__init__(cbpi, id, props)
        self.running = True
        self.value = 0
        self.lastvalue = 100
        # get properties
        self.base_url = self.props.get("base_url", "http://127.0.0.1:8000/api")
        self.debounce_time = self.props.get("debounce_time", 100)
        self.gpio_pin = self.props.get("gpio_pin", "disabled")
        self.method = self.props.get("method", "POST")
        self.command_string = self.props.get("command_string", "/step/next")
        self.url = f"{self.base_url}{self.command_string}"
        self.update_needed = True

        # if not disabled register the interrupt
        if (self.gpio_pin != "disabled"):
            logger.info(f"GPIOButton - START : register GPIO pin {self.gpio_pin} interrupt")
            GPIO.setup(int(self.gpio_pin), GPIO.IN , pull_up_down = GPIO.PUD_DOWN)
            GPIO.remove_event_detect(int(self.gpio_pin))
            GPIO.add_event_detect(int(self.gpio_pin), GPIO.BOTH, callback=self.IO_interrupt, bouncetime=int(self.debounce_time))
    
    def IO_interrupt(self, channel):
        if int(channel) == int(self.gpio_pin):
            if GPIO.input(channel) == GPIO.HIGH:
                self.call_api()
                self.value = 100
                self.update_needed = True
                logger.info("GPIO - button pushed %s" % (self.value))
            else:
                self.value = 0
                self.update_needed = True
                logger.info("GPIO - button released %s" % (self.value))
    
    def call_api(self):
        logging.info("GPIO - IO number - %s - %s %s" % (self.gpio_pin, self.method, self.url))
        try:
            print(f"sending api request {self.method} -> {self.url} with headers: {headers} ")
            requests.request(self.method, self.url, headers = headers, timeout=5)
        except Exception as e:
            self.logger.error(f"api call '{self.url}' with method {self.method} threw the following error: {e}")
    
    async def run(self):
        while self.running is True:
            if (self.update_needed):
                self.push_update(self.value)
                self.log_data(self.id, self.value)
            await asyncio.sleep(1)
    
    @action(key="test_api_call", parameters=[])
    async def testApiCall(self, **kwargs):
        logger.warning("API CALL TRIGGERED BY TEST API CALL FUNCTION FOR")
        self.call_api()

    def stop(self):
        self.running = False
        logger.info(f"GPIOButton - STOP : unregister GPIO pin {self.gpio_pin} interrupt")
        GPIO.cleanup([int(self.gpio_pin)])
        GPIO.remove_event_detect(int(self.gpio_pin))

def setup(cbpi):
    cbpi.plugin.register("GPIOButton", GPIOButtonSensor)
