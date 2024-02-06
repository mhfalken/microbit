# Michael Hansen 2020, Coding Pirates Furesoe, Denmark, www.rclab.dk
from microbit import *
import neopixel
from utime import ticks_us, sleep_us
from micropython import const

MODEL_AUTO = const(0)
MODEL_CLASSIC = const(1)
MODEL_XL = const(2)
LEFT = const(0)
RIGHT = const(1)

class bitbot:
    modelType = MODEL_AUTO
    scale = 2
    sonar = pin15
    lastDist = 2000

    def __init__(self):
        self.modelType = MODEL_XL
        try:
            i2c.read(0x1C, 1)[0]
        except:
            self.modelType = MODEL_CLASSIC
        self.scale = 1
        try:
            speaker.on()
        except:
            self.scale = 4

    def SetModel(self, modelType):
        self.modelType = modelType

    def GetModel(self):
        return self.modelType

    def Drive(self, left, right):
        """ Motor control: [-100, 100] """
        if left >= 0:
            pin8.write_digital(0)
        else:
            pin8.write_digital(1)
        if right >= 0:
            pin12.write_digital(0)
        else:
            pin12.write_digital(1)

        a_left = abs(left)
        if a_left > 0:
            a_left = 50 + int(a_left * 9)
        if left < 0:
            a_left = 1023 - a_left
        if self.modelType == MODEL_CLASSIC:
            pin0.write_analog(a_left)
        else:
            pin16.write_analog(a_left)

        a_right = abs(right)
        if a_right > 0:
            a_right = 50 + int(a_right * 9)
        if right < 0:
            a_right = 1023 - a_right
        if self.modelType == MODEL_CLASSIC:
            pin1.write_analog(a_right)
        else:
            pin14.write_analog(a_right)

    def DriveOffset(self, leftAdd):  # TT
        """ TBD """
        pass

    def ReadLine(self, sensor):
        """ True if dark line """
        if self.modelType == MODEL_CLASSIC:
            if sensor == LEFT:
                return pin11.read_digital() == 0
            else:
                return pin5.read_digital() == 0
        else:   # XL
            value = i2c.read(0x1C, 1)[0]
            return (value & (1 << sensor)) > 0

    def ReadLight(self, sensor):
        """ Return [0-100] """
        if self.modelType == MODEL_CLASSIC:
            if sensor == LEFT:
                pin16.write_digital(0)
            else:
                pin16.write_digital(1)
            return int(pin2.read_analog() / 10)
        else:   # XL
            if sensor == LEFT:
                return int(pin2.read_analog() / 10)
            else:
                return int(pin1.read_analog() / 10)

    def Sonar(self, max=100):
        """ Return cm """
        self.sonar.write_digital(1) # Send Ping
        sleep_us(10)
        self.sonar.write_digital(0)
        self.sonar.set_pull(self.sonar.NO_PULL)
        i = 0
        while True:
            if self.sonar.read_digital() == 1:  # Ping cleared
                break
            sleep_us(1)
            if (i == 300):
                return self.lastDist
            i += 1
        start = ticks_us()
        i = 0
        while True:
            if self.sonar.read_digital() == 0:  # wait Echo
                break
            sleep_us(1)
            if i == (max/self.scale):
                break
            i += 1
        end = ticks_us()
        echo = end-start
        distance = int(0.01715 * echo)
        if distance > max:
            distance = max
        self.lastDist = distance
        return distance

    def Buzzer(self, value):
        if self.modelType == MODEL_CLASSIC:
            pin14.write_digital(value > 0)
        else:
            pin0.write_digital(value > 0)

    def NeoPixel(self):
        return neopixel.NeoPixel(pin13, 12)