"""
This module contains the functions to control the stepper motors.
"""
import time
import smbus


# I²C Configuration: Typically bus 1 on a Raspberry Pi
I2C_BUS_NUMBER = 1
I2C_SLAVE_ADDRESS = 0x08  # This address MUST match the address in the Arduino sketch

class StepperMotorController:
    """
    This class sends I²C commands to the Arduino.
    Supported commands:
      - TOGGLE
      - SETUP
      - CLEANUP
      - ROTATE <steps> <direction> <delayInSec>
      - MOVE <direction> <speed> <steps>
    """
    def __init__(self, bus_number=I2C_BUS_NUMBER, slave_address=I2C_SLAVE_ADDRESS):
        self.bus = smbus.SMBus(bus_number)
        self.slave_address = slave_address
        time.sleep(0.1)
        print(f"I²C connection established to address 0x{slave_address:02X} on bus {bus_number}")

    def send_command(self, command: str):
        """
        Converts the command string into a list of bytes and sends it via I²C.
        """
        data = list(command.encode('utf-8'))
        try:
            # We send the data to a dummy register (0)
            self.bus.write_i2c_block_data(self.slave_address, 0, data)
            print(f"Command sent: {command}")
        except OSError as e:
            print(f"I²C communication error: {e}")
        except ValueError as e:
            print(f"Invalid data format: {e}")
        time.sleep(0.1)

    def toggle_io_band(self):
        """Toggles the IO band state."""
        self.send_command("TOGGLE")

    def setup_pins(self):
        """Cleans up the Aduino pins."""
        self.send_command("SETUP")

    def cleanup(self):
        """Cleans up the GPIO pins."""
        self.send_command("CLEANUP")

    def rotate(self, steps: int, direction: str, delay_in_sec: float):
        """
        Rotates the motor by a specified number of steps in the given direction.
        
        Args:
            steps (int): Number of steps to move.
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            delay (float): Delay between each step (controls speed).
        """
        command = f"ROTATE {steps} {direction.upper()} {delay_in_sec}"
        self.send_command(command)

    def move_robot(self, direction: str, speed: int, steps: int):
        """
        Moves the robot in the specified direction by the specified amount of steps.
        :return: False if the robot would move out of the LED strip.
        
        Args:
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            speed (int): The speed of the robot.
            steps (int): The amount of steps the robot should move.
        """
        command = f"MOVE {direction.upper()} {speed} {steps}"
        self.send_command(command)

# def main():
#    controller = StepperMotorController()
#    while True:
#        print("\nPlease choose a command:")
#        print("1: TOGGLE")
#        print("2: SETUP")
#        print("3: CLEANUP")
#        print("4: ROTATE <steps> <direction> <delayInSec>")
#        print("5: MOVE <direction> <speed> <steps>")
#        print("q: Quit")
#        choice = input("Your choice: ").strip().lower()
#
#        if choice == 'q':
#            print("Exiting program.")
#            break
#        elif choice == '1':
#            controller.toggle_io_band()
#        elif choice == '2':
#            controller.setup_pins()
#        elif choice == '3':
#            controller.cleanup()
#        elif choice == '4':
#            try:
#                steps = int(input("Number of steps: "))
#                direction = input("Direction (LEFT/RIGHT): ").strip()
#                delay_input = input("Delay in seconds (e.g., 0.01): ").strip()
#                delay_in_sec = float(delay_input)
#                controller.rotate(steps, direction, delay_in_sec)
#            except ValueError:
#                print("Invalid input for ROTATE!")
#        elif choice == '5':
#            try:
#                direction = input("Direction (LEFT/RIGHT): ").strip()
#                speed = int(input("Speed (integer): "))
#                steps = int(input("Number of steps: "))
#                controller.move_robot(direction, speed, steps)
#            except ValueError:
#                print("Invalid input for MOVE!")
#        else:
#            print("Invalid choice. Please try again.")
#
#if __name__ == "__main__":
#    main()
