import board
from adafruit_seesaw import seesaw, neopixel

i2c = board.I2C()
encoder_board = seesaw.Seesaw(i2c, addr=0x36)

pixel = neopixel.NeoPixel(encoder_board, 6, 1)
pixel.brightness = 0.3

# Light pink!
pixel.fill((255, 80, 160))

print("NeoPixel should now be glowing pink!")