import os
import struct
import subprocess
import tempfile
import math
import numpy as np
import time
from rpi_ws281x import PixelStrip, Color

# CAVA configuration
BARS_NUMBER = 12
BARS_HEIGHT = 10
RAW_TARGET = "/dev/stdout"
OUTPUT_BIT_FORMAT = "16bit"
RATE = 44100

conpat = """
[general]
bars = %d

[output]
method = raw
channels = mono
raw_target = /dev/stdout
data_format = ascii
bit_format = 16bit
ascii_max_range = %d

[smoothing]
monstercat = 1
waves = 1
noise_reduction = 0.3
"""

config = conpat % (BARS_NUMBER, BARS_HEIGHT)

# LED strip configuration:
LED_COUNT = BARS_NUMBER * BARS_HEIGHT        # Number of LED pixels.
#LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def run():
    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()
        
        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        source = process.stdout

        while True:
            line = source.readline()
            if not line:
                break;
            data = line.decode('UTF-8').rstrip().split(';')[:-1]
            sample = [int(i) for i in data]
            showLed(sample)
            print(sample) 

def resetLed():
    color = Color(0,0,0)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)

def showLed(sample):
    if len(set(sample)) == 1:
        return  

    resetLed();
    color = Color(0, 1, 1);
    for i, height in enumerate(sample):
        for j in range(height):
            strip.setPixelColor(i * BARS_HEIGHT + j, color)
    strip.show() 

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
if __name__ == "__main__":
    strip.begin()
    run();
