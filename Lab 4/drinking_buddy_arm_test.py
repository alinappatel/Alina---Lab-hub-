import pi_servo_hat
import time

servo = pi_servo_hat.PiServoHat()
servo.restart()

channel = 0

try:
    print("Moving to 60 degrees...")
    servo.move_servo_position(channel, 60)
    time.sleep(2)

    for angle in [55, 50, 45, 50, 55, 60]:
        input(f"Press Enter to move to {angle} degrees...")
        servo.move_servo_position(channel, angle)
        time.sleep(0.5)

    print("Test complete!")

except KeyboardInterrupt:
    print("\nTest stopped.")
