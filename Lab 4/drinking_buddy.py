import time
import qwiic_proximity
import pi_servo_hat

# Servo settings
SERVO_CHANNEL = 0
REST_ANGLE = 80
CHEERS_ANGLE = 0

# Sensor settings, based on our tests
GLASS_PRESENT = 1095
GLASS_REMOVED = 1092

# Initialize proximity sensor
sensor = qwiic_proximity.QwiicProximity()

if not sensor.connected:
    raise RuntimeError("VCNL4040 proximity sensor not found")

sensor.begin()

# Initialize servo
servo = pi_servo_hat.PiServoHat()
servo.restart()


def move_slowly(start, end, delay=0.025):
    """Move the servo smoothly between two angles."""
    step = 1 if end > start else -1

    for angle in range(start, end + step, step):
        servo.move_servo_position(SERVO_CHANNEL, angle)
        time.sleep(delay)


def cheers():
    """Buddy raises its shot, pauses, then lowers it."""
    print("CHEERS! Buddy raises its shot!")

    move_slowly(REST_ANGLE, CHEERS_ANGLE)
    time.sleep(1)

    move_slowly(CHEERS_ANGLE, REST_ANGLE)
    print("Buddy lowers its shot.")


print("Drinking Buddy is ready!")
print("Place your glass on the coaster to begin.")

servo.move_servo_position(SERVO_CHANNEL, REST_ANGLE)
time.sleep(1)

# Initially unarmed until a glass is detected on the coaster
glass_present = False
present_count = 0
removed_count = 0

try:
    while True:
        proximity = sensor.get_proximity()

        # Confirm the glass has returned
        if proximity >= GLASS_PRESENT:
            present_count += 1
            removed_count = 0

            if present_count >= 3 and not glass_present:
                glass_present = True
                print("Glass detected. Ready to cheers!")

        # Confirm the glass has been lifted
        elif proximity <= GLASS_REMOVED:
            removed_count += 1
            present_count = 0

            if removed_count >= 3 and glass_present:
                glass_present = False
                cheers()

        else:
            # Ignore readings between the thresholds
            present_count = 0
            removed_count = 0

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping Drinking Buddy.")

finally:
    servo.move_servo_position(SERVO_CHANNEL, REST_ANGLE)
    print("Buddy returned to resting position.")
