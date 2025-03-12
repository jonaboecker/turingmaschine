"""
This module contains the state machine to control the robot.
The filename is under monument protection, you are not allowed to change it.
"""
import time
# pylint: disable=too-many-instance-attributes
from threading import Lock

import assets
import hardware_control as hc

class StateMachine:
    """
    This class is used to control the robot with the Turing machine.
    :arg tm_code: turing_machine = {
        "name": "",
        "init": "",
        "accept": set(),
        "state_transitions": defaultdict(dict),
        "errors": [],
        "warnings": []
    }
    """

    def __init__(self, tm_code, app):
        self.stepper = hc.StepperMotorController(app)
        self.accept_states = tm_code['accept']
        self.current_state = tm_code['init']
        self.state_transitions = tm_code['state_transitions']
        self.program_name = tm_code['name']
        self.errors = []
        self.speed = 5
        self.steps = 0
        self.running = False
        self.pause = False
        self.should_stop = False
        self.lock = Lock()
        self._listeners = []  # Observer for Changes
        self.position = 0
        # Flask app for config. Config changes are just supported after StateMachine restart.
        self.app = app

    def add_listener(self, callback):
        """Registriere eine Callback-Funktion, die bei Änderungen aufgerufen wird."""
        self._listeners.append(callback)

    def _notify_listeners(self):
        """Benachrichtigt alle registrierten Listener über eine Änderung."""
        for callback in self._listeners:
            callback()

    def home_robot(self) -> bool:
        """Homing the robot"""
        if not self.single_home_step(False, assets.ROBOT_DIRECTIONS.LEFT, 10, 30):
            return False
        if not self.single_home_step(True, assets.ROBOT_DIRECTIONS.RIGHT, 5, 20):
            return False
        if not self.single_home_step(False, assets.ROBOT_DIRECTIONS.LEFT, 1, 10):
            return False
        # Go to first LED
        if not self.stepper.move_robot(assets.ROBOT_DIRECTIONS.RIGHT, 5,
                                       self.app.config['STEPS_BETWEEN_HOME_TO_FIRST_LED']):
            return False
        self.execute_with_lock_and_notify(lambda: (setattr(self, 'position', 1)))
        print("Position set to " + str(self.position))
        print("Robot homed")
        return True

    def single_home_step(self, lb_state: bool, direction: assets.ROBOT_DIRECTIONS, speed: int,
                         steps: int) -> bool:
        """Single step for homing the robot. Drive until the light barrier toggles."""
        while self.stepper.get_lb_state() == lb_state:
            if not self.stepper.move_robot(direction, speed, steps):
                return False
            self.pause_machine()
            if self.should_stop:
                print("Robot homing stopped by user")
                return False
        return True

    def go_to_first_color(self):
        """
        Moving the robot to the first color
        Returns:
            bool: True if the robot reached the first color,
                  False if the robot would move out of the LED strip.
        """
        print("Robot moving to first color")
        while self.stepper.get_color() == assets.IO_BAND_COLORS.BLANK:
            self.pause_machine()
            if self.should_stop:
                print("Robot go_to_first_color stopped by user")
                return False
            new_position = self.stepper.move_robot_led_step(assets.ROBOT_DIRECTIONS.RIGHT,
                                                            self.speed)
            self.execute_with_lock_and_notify(lambda: (setattr(self, 'position', new_position)))
            print(f"Position set to {self.position}  new Position was {new_position}")
            if self.position <= 0:
                return False
        return True

    def execute_with_lock_and_notify(self, task):
        """
        Führt die angegebene Funktion `task` unter Verwendung des Locks aus
        und benachrichtigt anschließend die Listener.

        :param task: Eine Callback-Funktion, die die eigentliche Arbeit ausführt.
        """
        with self.lock:
            task()  # Führe die Arbeit aus
            self._notify_listeners()

    def single_step(self):
        """
        Executes a single step of the Turing machine.
        :returns:
            bool: True if the step was executed successfully,
                  False if there was no transition for the current step.
        """
        transition = self.state_transitions.get((self.current_state, self.stepper.get_color()))
        if transition is None:
            print(f"No transition for {self.current_state}, color {self.stepper.get_color()}")
            self.execute_with_lock_and_notify(
                lambda: self.errors.append("Dein Turing Programm hat einen Reject State erreicht."))
            return False
        self.execute_with_lock_and_notify(
            lambda: setattr(self, 'current_state', transition['new_state']))
        toggle_retry = 0
        while self.stepper.get_color() != transition['write_symbol']:
            if toggle_retry >= self.app.config['TOGGLE_IO_BAND_RETRYS']:
                self.execute_with_lock_and_notify(
                    lambda: self.errors.append("Das IO-Band kann nicht bearbeitet werden."))
                return False
            toggle_retry += 1
            self.stepper.toggle_io_band()
        new_position = self.stepper.move_robot_led_step(transition['move'], self.speed)
        self.execute_with_lock_and_notify(lambda: (setattr(self, 'position', new_position)))
        print(f"Position set to {self.position}  new Position was {new_position}")
        if self.position == -2:
            self.execute_with_lock_and_notify(
                lambda: self.errors.append("Dein Turing Programm ist zu groß für das Band."))
            print("Band ended")
            return False
        if self.position < 0:
            self.execute_with_lock_and_notify(
                lambda: self.errors.append("Es gab ein Problem beim bewegen des Roboters."))
            print(f"Error while moving the robot, error code: {self.position}")
            return False
        self.execute_with_lock_and_notify(lambda: setattr(self, 'steps', self.steps + 1))
        return True

    def run(self):
        """
        Run the state machine
        :returns:
            bool: True if the tm reached an accept state,
                  False if there accept wasn't reached, reason is saved in self.errors.
        """
        self.execute_with_lock_and_notify(
            lambda: (setattr(self, 'running', True), setattr(self, 'should_stop', False)))
        if not self.home_robot():
            print("Robot homing failed")
            self.execute_with_lock_and_notify(
                lambda: (setattr(self, 'running', False),
                         setattr(self, 'pause', False),
                         setattr(self, 'should_stop', False),
                         self.errors.append("Der Roboter konnte nicht homen.")))
            return False
        self.pause_machine()
        if self.should_stop:
            self.stop_by_flag()
            return False
        if not self.go_to_first_color():
            print("Blank io_band, Robot would move out of the LED strip")
            new_position = self.stepper.move_robot_led_step(assets.ROBOT_DIRECTIONS.LEFT,
                                                            self.speed,
                                                            int(self.app.config['LED_AMOUNT'] / 2))
            self.execute_with_lock_and_notify(lambda: (setattr(self, 'position', new_position)))
            if self.position <= 0:
                self.execute_with_lock_and_notify(
                    lambda: self.errors.append("Es gab ein Problem beim bewegen des Roboters."))
                print(f"Error while moving the robot, error code: {self.position}")
                return False
        print("Robot reached the start of input")
        while self.current_state not in self.accept_states:
            self.pause_machine()
            if self.should_stop:
                self.stop_by_flag()
                return False
            print(f"Current state: {self.current_state}")
            if not self.single_step():
                print(self.errors)
                self.execute_with_lock_and_notify(
                    lambda: (setattr(self, 'running', False),
                             setattr(self, 'pause', False),
                             setattr(self, 'should_stop', False),
                             self.errors.append(
                                 "Dein Turing Programm wurde aufgrund eines Fehlers gestoppt.")))
                return False
        print("Robot reached an accept state")
        self.execute_with_lock_and_notify(lambda: setattr(self, 'running', False))
        return True

    def pause_machine(self):
        """Pause the state machine"""
        while self.pause:
            if self.should_stop:
                return
            time.sleep(0.1)

    def pause_program(self):
        """Setting the flag to Pause the state machine"""
        self.execute_with_lock_and_notify(lambda: setattr(self, 'pause', True))
        print("Robot paused")

    def resume_program(self):
        """Setting the flag to Resume the state machine"""
        self.execute_with_lock_and_notify(lambda: setattr(self, 'pause', False))
        print("Robot resumed")

    def stop_program(self):
        """Stop the state machine at the next opportunity, set the should_stop flag"""
        self.execute_with_lock_and_notify(
            lambda: (setattr(self, 'should_stop', True), self.errors.append(
                "Dein Turing Programm wird bei nächster Gelegenheit gestoppt.")))
        print("should_stop flag set, Robot will stop soon")

    def change_speed(self, speed):
        """Change the speed of the robot"""
        self.execute_with_lock_and_notify(lambda: setattr(self, 'speed', speed))
        print(f"Speed changed to {speed}")

    def stop_by_flag(self):
        """Stop the state machine after the should_stop flag was set"""
        self.execute_with_lock_and_notify(
            lambda: (setattr(self, 'running', False), setattr(self, 'pause', False),
                     setattr(self, 'should_stop', False),
                     self.errors.append("Das Turing Programm wurde vom Benutzer gestoppt.")))
        print("Robot stopped by should_stop flag")
