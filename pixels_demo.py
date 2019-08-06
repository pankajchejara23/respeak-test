import time
from pixels import Pixels, pixels

from google_home_led_pattern import GoogleHomeLedPattern

if __name__ == '__main__':

    pixels.pattern = GoogleHomeLedPattern(show=pixels.show)

    while True:

        try:
            pixels.wakeup()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)
