import pi_servo_hat
import time

servo = pi_servo_hat.PiServoHat()
servo.restart()

CHANNEL = 0
REST = 80
CHEERS = 0

def move_slowly(start, end):
    step = 1 if end > start else -1
    for angle in range(start, end + step, step):
        servo.move_servo_position(CHANNEL, angle)
        time.sleep(0.025)

try:
    # Start with arm lowered
    servo.move_servo_position(CHANNEL, REST)
    time.sleep(1)

    input("Press Enter to cheers!")

    move_slowly(REST, CHEERS)
    time.sleep(1.5)
    move_slowly(CHEERS, REST)

    print("Cheers complete!")

except KeyboardInterrupt:
    servo.move_servo_position(CHANNEL, REST)
    print("Stopped.")