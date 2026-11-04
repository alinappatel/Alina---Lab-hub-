import pi_servo_hat

servo = pi_servo_hat.PiServoHat()
servo.restart()

print("Drinking Buddy manual servo control")

while True:
    try:
        value = input("Enter angle (0-120), or q: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nStopped.")
        break

    if value.lower() == "q":
        break

    try:
        angle = int(value)
    except ValueError:
        print("Enter a whole number.")
        continue

    if 0 <= angle <= 120:
        servo.move_servo_position(0, angle)
        print("Moved to", angle)
    else:
        print("Enter an angle between 0 and 120.")
