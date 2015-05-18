__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import os
import time
import threading

class GPIO:
    def __init__(self):
        led1 = 61
        led2 = 44
        led3 = 68
        led4 = 67
        self.led_ports = [led1, led2, led3, led4]
        button_1 = 49
        button_2 = 112
        button_3 = 51
        button_4 = 7
        button_left = 48
        self.button_ports = [button_1, button_2, button_3, button_4, button_left]
        self.gpio_path = "/sys/class/gpio/gpio"
        self.led_states = [0, 0, 0, 0]
        self.blink_thread = threading.Thread(target=self._blink_task)
        self.blink_thread.setDaemon(1)

    def set_led(self, led_nr, value):
        value = abs(value-1)
        self.led_states[led_nr] = value
        self._set_led(led_nr, value)

    def _set_led(self, led_nr, value):
        led_path = self.gpio_path + str(self.led_ports[led_nr]) + '/'
        os.system("echo %s > %svalue" % (value, led_path))

    def get_button(self, button_nr):
        button_path = self.gpio_path + str(self.button_ports[button_nr]) + '/value'
        with open(button_path) as f:
            return abs(int(f.read())-1)

    def blink_led(self):
        self.blink_thread.start()

    def _blink_task(self):
        while True:
            for led_nr in range(4):
                self._set_led(led_nr, 1)
            time.sleep(0.1)
            for led_nr in range(4):
                self._set_led(led_nr, self.led_states[led_nr])
            time.sleep(0.1)

if __name__ == "__main__":
    gpio = GPIO()
    gpio.set_led(0, 0)
    gpio.set_led(1, 1)
    time.sleep(2)
    for i in (0, 1, 2, 3):
        value = gpio.get_button(i)
        gpio.set_led(i, value)
    time.sleep(3)
    gpio.blink_led()
    time.sleep(5)
