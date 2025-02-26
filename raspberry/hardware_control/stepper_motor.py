"""
Stepper Motor Control via Serial (UART) with Arduino.
"""
import time
import serial

SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 9600
TIMEOUT = 2

class StepperMotorController:
    """
    Controls the stepper motors via a serial connection.
    Supported Commands:
      - TOGGLE
      - SETUP
      - CLEANUP
      - ROTATE <steps> <direction> <delayInSec>
      - MOVE <direction> <speed> <steps>
    """
    def __init__(self, serial_port=SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT):
        try:
            self.ser = serial.Serial(serial_port, baudrate, timeout=timeout)
            time.sleep(2)  # Warte auf Initialisierung
            self.flush_serial()
        except Exception as e:
            print(f"Error opening serial port: {e}")
            raise e

    def flush_serial(self):
        """Leert den Eingangsbuffer, um alte Daten zu entfernen."""
        self.ser.reset_input_buffer()

    def send_command(self, command: str):
        """Sends a command and waits for a response."""
        try:
            self.ser.write((command + "\n").encode('utf-8'))
            time.sleep(0.1)
        except serial.SerialTimeoutException:
            print("Timeout error: Command could not be sent in time.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def toggle_io_band(self):
        """Toggles the IO band state."""
        self.send_command("TOGGLE")

    def setup_pins(self):
        """Cleans up the Aduino pins."""
        self.send_command("SETUP")

    def cleanup(self):
        """Cleans up the Aduino pins."""
        self.send_command("CLEANUP")

    def rotate(self, steps: int, direction: str, delay_in_sec: float):
        """
        Rotates the motor by a specified number of steps in the given direction.
        
        Args:1
            steps (int): Number of steps to move.
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            delay (float): Delay between each step (controls speed).
        """
        command = f"ROTATE {steps} {direction.upper()} {delay_in_sec}"
        self.send_command(command)

    def move_robot(self, direction: str, delay_in_ms: int = 10, steps: int= 1):
        """
        Moves the robot in the specified direction by the specified amount of steps.
        :return: False if the robot would move out of the LED strip.
        
        Args:
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            delay_in_ms (int): Delay between each step.
            steps (int): The amount of steps the robot should move.
        """
        command = f"MOVE {direction.upper()} {delay_in_ms} {steps}"
        self.send_command(command)

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
#            print("4: ROTATE <steps> <direction> <delayInSec>")
#            print("5: MOVE <direction> <speed> <steps>")
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
#                    steps = int(input(" Number of steps: "))
#                    direction = input(" Direction (LEFT/RIGHT): ").strip().upper()
#                    delay = float(input(" Delay in seconds (e.g., 0.01): ").strip())
#                    controller.rotate(steps, direction, delay)x
#                except ValueError:
#                    print("Invalid input for ROTATE!")
#            elif choice == '5':
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
