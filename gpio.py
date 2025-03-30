import RPi.GPIO as GPIO
from time import DSHOW

class StepperMotor:
    def __init__(self, dir_pin=10, step_pin=8, steps_per_revolution=200):
        """Initialize the stepper motor with specified pins and steps per revolution"""
        self.dir_pin = dir_pin  # Direction pin
        self.step_pin = step_pin  # Step pin
        self.steps_per_revolution = steps_per_revolution  # Steps for a full 360-degree revolution
        self.step_delay = 0.005  # Delay between steps (in seconds)
        self.direction_switch_delay = 0.5  # Delay when switching direction (in seconds)

        # Constants for direction
        self.CW = 1  # Clockwise
        self.CCW = 0  # Counterclockwise

        # Calculate degrees per step
        self.degrees_per_step = 360.0 / self.steps_per_revolution  # e.g., 1.8 degrees per step for 200 steps

        # Setup GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)

    def rotate_angle(self, angle):
        """Rotate the motor by a specified angle (in degrees). Positive angle for CW, negative for CCW"""
        # Calculate the number of steps needed for the given angle
        steps = int(abs(angle) / self.degrees_per_step)
        if steps == 0:
            print("Angle too small to move.")
            return

        # Determine direction based on the sign of the angle
        direction = self.CW if angle >= 0 else self.CCW

        # Set the direction
        GPIO.output(self.dir_pin, direction)
        sleep(self.direction_switch_delay)  # Wait for the motor to stabilize after direction change

        # Perform the steps
        print(f"Rotating {angle} degrees ({steps} steps) in {'CW' if direction == self.CW else 'CCW'} direction")
        for _ in range(steps):
            GPIO.output(self.step_pin, GPIO.HIGH)
            sleep(self.step_delay)
            GPIO.output(self.step_pin, GPIO.LOW)
            sleep(self.step_delay)

    def cleanup(self):
        """Cleanup GPIO resources"""
        print("Cleaning up GPIO")
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    try:
        # Initialize the stepper motor
        motor = StepperMotor(dir_pin=10, step_pin=8, steps_per_revolution=200)

        # Rotate by specific angles
        motor.rotate_angle(90)  # Rotate 90 degrees clockwise
        sleep(1)  # Wait before the next movement
        motor.rotate_angle(-90)  # Rotate 90 degrees counterclockwise
        sleep(1)
        motor.rotate_angle(180)  # Rotate 180 degrees clockwise

    except KeyboardInterrupt:
        print("Program interrupted by user")
        motor.cleanup()
    except Exception as e:
        print(f"An error occurred: {e}")
        motor.cleanup()