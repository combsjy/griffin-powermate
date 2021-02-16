from pywinusb.hid import HidDeviceFilter
from ctypes import *


def find_griffin_powermate():
    return GriffinPowermate.find_all()


class GriffinPowermate(object):
    VENDOR = 0x077d
    PRODUCT = 0x0410
    MOVE_LEFT = -1
    MOVE_RIGHT = 1

    def __init__(self, raw_device):
        self.__device = raw_device
        self.__device.set_raw_data_handler(
            lambda raw_data: self.__internal_listener(raw_data))
        self.__is_button_down = False

        # events:
        #  on_up
        #  on_down
        #  on_pressed
        #  on_released
        #  on_up_while_pressed
        #  on_down_while_down

    @property
    def is_button_down(self):
        return self.__is_button_down

    def __on_up(self, offset):
        self.on_up(offset)

    def on_up(self, offset):
        print('Moved up {}'.format(offset))

    def __on_down(self, offset):
        self.on_down(offset)

    def on_down(self, offset):
        print('Moved down {}'.format(offset))

    def __on_pressed(self):
        self.__is_button_down = True
        self.on_pressed()

    def on_pressed(self):
        print('Button pressed')

    def __on_released(self):
        self.__is_button_down = False
        self.on_released()

    def on_released(self):
        print('Button released')

    def __on_up_while_pressed(self, offset):
        self.__on_up(offset)

    def __on_down_while_pressed(self, offset):
        self.__on_down(offset)

    @classmethod
    def find_all(cls):
        return [cls(device) for device in
                HidDeviceFilter(vendor_id=cls.VENDOR,
                                product_id=cls.PRODUCT).get_devices()]

    def __internal_listener(self, raw_data):
        """
        [0, button_status, move, 0, bright, pulse_status, pulse_value]
        """
        direction_delta = c_int8(raw_data[2]).value
        button_state = raw_data[1]

        if direction_delta > 0:
            if self.is_button_down:
                self.__on_up_while_pressed(direction_delta)
            else:
                self.__on_up(direction_delta)
        elif direction_delta < 0:
            direction_delta *= -1
            if self.is_button_down:
                self.__on_down_while_pressed(direction_delta)
            else:
                self.__on_down(direction_delta)
        else:
            if self.__is_button_down and button_state == 0:
                self.__on_released()
            elif not self.__is_button_down and button_state == 1:
                self.__on_pressed()
            else:
                raise Exception('invalid condition')

    def is_plugged(self):
        return self.__device.is_plugged()

    def open(self):
        if not self.__device.is_opened():
            self.__device.open()

    def close(self):
        if self.__device.is_opened():
            self.__device.close()

    def set_brightness(self, bright):
        # alternative: device.send_output_report([0, bright])
        self.__device.send_feature_report(
            [0, 0x41, 0x01, 0x01, 0x00, bright % 255, 0x00, 0x00, 0x00])

    def set_led_pulsing_status(self, on=True):
        # led pulsing on/off
        self.__device.send_feature_report([0, 0x41, 0x01, 0x03, 0x00, 0x01
                                           if on else 0x00, 0x00, 0x00, 0x00])

    def set_led_pulsing_default(self):
        self.__device.send_feature_report(
            [0, 0x41, 0x01, 0x04, 0x00, 0x01, 0x00, 0x00, 0x00])
