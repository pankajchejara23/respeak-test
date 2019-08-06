import time
import sys
import webrtcvad
import numpy as np
from mic_array import MicArray
import apa102
from gpiozero import LED
import wave
import pyaudio

import datetime
from google_home_led_pattern import GoogleHomeLedPattern
from pixels import Pixels, pixels

dev = apa102.APA102(num_led=12)

wavframes = []


file = open('speaking.csv','w')








print("Initiating microphone array....")
print("Wait for LED's light indication...")
#pixels.wakeup()



RATE = 16000
CHANNELS = 4
VAD_FRAMES = 10     # ms
DOA_FRAMES = 200    # ms

audInstance = None

def show(direction):
    position = int((direction + 15) / (360 / 12)) % 12

    data = [0, 0, 0, 0] * 12
    
    
    for i in range(12):
        if i==position:
            print("Position: %d,%d,%d"%((i+12-1)%12,i,(i+1)%12))
            dev.set_pixel(i, 0, 48, 0)
        elif i==(position+12-1)%12:
            dev.set_pixel(i, 10, 0, 0)
        elif i==(position+1)%12:
            dev.set_pixel(i, 10, 0, 0)
        else:
            dev.set_pixel(i, 0, 0, 0)
        dev.show()



def main():
    vad = webrtcvad.Vad(3)

    speech_count = 0
    chunks = []
    doa_chunks = int(DOA_FRAMES / VAD_FRAMES)

    try:
        with MicArray(RATE, CHANNELS, RATE * VAD_FRAMES / 1000)  as mic:
            audInstance = mic.pyaudio_instance
            for chunk in mic.read_chunks():
                wavframes.append(chunk.tostring())
                # Use single channel audio to detect voice activity 
                if vad.is_speech(chunk[0::CHANNELS].tobytes(), RATE):
                    speech_count += 1


                chunks.append(chunk)
                if len(chunks) == doa_chunks:
                    if speech_count > (doa_chunks / 2):
                        frames = np.concatenate(chunks)
                        direction = mic.get_direction(frames)
                        show(direction)
                        now = datetime.datetime.now()
                        file.write('{},{}\n'.format(now.strftime("%H:%M:%S %d-%m-%Y"),int(direction)))
                        print('\n{},{}'.format(now.strftime("%H:%M:%S %d-%m-%Y"),int(direction)))

                    speech_count = 0
                    chunks = []

    except KeyboardInterrupt:
        file.close()
        wav = wave.open('session.wav','wb')
        wav.setnchannels(CHANNELS)
        wav.setsampwidth(audInstance.get_sample_size(pyaudio.paInt16))
        wav.setframerate(RATE)
        wav.writeframes(b''.join(wavframes))
        wav.close()
        
        print(" Audio recording is saved in file: session.wav")
        print(" Direction of arrival recorded in file: speaking.csv")
        
        
        print("Good Bye.....")
         
   


if __name__ == '__main__':
    main()
