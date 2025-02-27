"""
Stepper Motor Control via Serial (UART) with Arduino.
"""
import time
import platform

import assets

if platform.system() == "Linux":
    import serial

SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 9600
TIMEOUT = 2

SPEED_DELAY_MAP = {
    1: 55,
    2: 50,
    3: 45,
    4: 40,
    5: 35,
    6: 30,
    7: 25,
    8: 20,
    9: 15,
    10: 10
}

class StepperMotorController:
    """
    Controls the stepper motors via a serial connection.
    Supported Commands:
      - TOGGLE
      - SETUP
      - CLEANUP
      - MOVE <direction> <speed> <steps>
    """
    def __init__(self, serial_port=SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT):
        if platform.system() == "Linux":
            try:
                self.ser = serial.Serial(serial_port, baudrate, timeout=timeout)
                time.sleep(2)
                self.ser.reset_input_buffer()
            except Exception as e:
                print(f"Error opening serial port: {e}")
                raise e

    def send_command(self, command: str) -> int:
        """Sends a command and returns 1 if successful, 0 otherwise."""
        try:
            encoded_cmd = (command + "\n").encode('utf-8')
            bytes_written = self.ser.write(encoded_cmd)
            time.sleep(0.1)
            expected_bytes = len(encoded_cmd)
            return bytes_written == expected_bytes
        except serial.SerialTimeoutException:
            print("Timeout error: Command could not be sent in time.")
            return 0
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return 0

    def toggle_io_band(self):
        """Toggles the IO band state."""
        if platform.system() == "Linux":
            return self.send_command("TOGGLE")
        return False

    def setup_pins(self):
        """Cleans up the Aduino pins."""
        return self.send_command("SETUP")

    def cleanup(self):
        """Cleans up the Aduino pins."""
        return self.send_command("CLEANUP")

    def move_robot(self, direction: assets.ROBOT_DIRECTIONS, speed: int = 5, steps: int= 1):
        """
        Moves the robot in the specified direction by the specified amount of steps.
        :return: False if the robot would move out of the LED strip. Else True
        
        Args:
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            speed (int): int from 1 to 10 representing the robot-speed, 1 is slow 10 is fast.
            steps (int): The amount of steps the robot should move.
        """
        delay_in_ms = SPEED_DELAY_MAP.get(speed, 10)
        if platform.system() == "Linux":
            drict = "LEFT" if direction == assets.ROBOT_DIRECTIONS.LEFT else "RIGHT"
            command = f"MOVE {drict} {delay_in_ms} {steps}"
            return self.send_command(command)
        print(f"Move robot: direction: {direction} delay_in_ms: {delay_in_ms} steps: {steps}")
        time.sleep(delay_in_ms / 10)
        return True

#def main():
#    controller = None
#    try:
#        controller = StepperMotorController()
#
#       while True:
#            print("\n Choose a command:")
#            print("1: TOGGLE")
#            print("2: SETUP")
#            print("3: CLEANUP")
#            print("4: MOVE <direction> <speed> <steps>")
#            print("q: Quit")
#            choice = input("Your choice: ").strip().lower()
#
#            if choice == 'q':
#                print("Exiting program.")
#                break
#            elif choice == '1':
#                controller.toggle_io_band()
#            elif choice == '2':
#                controller.setup_pins()
#            elif choice == '3':
#                controller.cleanup()
#            elif choice == '4':
#                try:
#                    direction = input("Direction (LEFT/RIGHT): ").strip().upper()
#                    speed = int(input("Speed (integer): "))
#                    steps = int(input(" Number of steps: "))
#                    controller.move_robot(direction, speed, steps)
#                except ValueError:
#                    print("Invalid input for MOVE!")
#            else:
#                print("Invalid choice. Please try again.")
#
#    except KeyboardInterrupt:
#        print("\n Program interrupted by user.")
#    except Exception as e:
#        print(f"Error: {e}")
#    finally:
#        if controller:
#            controller.close()
#
#if __name__ == "__main__":
#    main()
