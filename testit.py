from griffin_powermate import GriffinPowermate, PressKey, ReleaseKey, KeyConstants

import time


class MyPowermate(GriffinPowermate):
    def on_pressed(self):
        PressKey(KeyConstants.VK_MEDIA_PLAY_PAUSE)
        print('overridden pressed event')

    def on_released(self):
        ReleaseKey(KeyConstants.VK_MEDIA_PLAY_PAUSE)
        print('overridden released event')

    def on_up(self, offset):
        for i in range(offset):
            PressKey(KeyConstants.VK_VOLUME_UP)
            ReleaseKey(KeyConstants.VK_VOLUME_UP)

    def on_down(self, offset):
        for i in range(offset):
            PressKey(KeyConstants.VK_VOLUME_DOWN)
            ReleaseKey(KeyConstants.VK_VOLUME_DOWN)


d = MyPowermate.find_all()[0]

d.open()


while True:
    time.sleep(5)


