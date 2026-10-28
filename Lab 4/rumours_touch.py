
import time
import board
import adafruit_mpr121

i2c = board.I2C()
mpr121 = adafruit_mpr121.MPR121(i2c)

songs = {
    7: "SILVER_SPRINGS",
    9: "NEVER_GOING_BACK_AGAIN",
    11: "SONGBIRD",
}

previous = {pin: False for pin in songs}

print("READY", flush=True)

try:
    while True:
        for pin, song in songs.items():
            touched = bool(mpr121[pin].value)

            if touched != previous[pin]:
                action = "DOWN" if touched else "UP"
                print(f"{action} {song}", flush=True)
                previous[pin] = touched

        time.sleep(0.03)

except KeyboardInterrupt:
    pass
