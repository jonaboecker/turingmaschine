"""
This module contains the state machine to control the robot.
"""
import time
# pylint: disable=too-many-instance-attributes
# pylint: todo: disable=fixme
from threading import Lock

import assets
import hardware_control.color_sensor as cs
import hardware_control.stepper_motor as sm
import hardware_control.light_barrier as lb


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

    def __init__(self, tm_code):
        self.stepper = sm.StepperMotorController()
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
        self._listeners = []  # Observer für Änderungen

    def add_listener(self, callback):
        """Registriere eine Callback-Funktion, die bei Änderungen aufgerufen wird."""
        self._listeners.append(callback)

    def _notify_listeners(self):
        """Benachrichtigt alle registrierten Listener über eine Änderung."""
        for callback in self._listeners:
            callback()

    def home_robot(self):
        """Homing the robot"""
        # todo: improve the homing
        while not lb.get_state():
            self.stepper.move_robot(assets.ROBOT_DIRECTIONS.LEFT, self.speed)
            self.pause_machine()
            if self.should_stop:
                print("Robot homing stopped by user")
                return
        print("Robot homed")

    def go_to_first_color(self):
        """
        Moving the robot to the first color
        Returns:
            bool: True if the robot reached the first color,
                  False if the robot would move out of the LED strip.
        """
        while cs.get_color() == assets.IO_BAND_COLORS.BLANK:
            self.pause_machine()
            if self.should_stop:
                print("Robot go_to_first_color stopped by user")
                return False
            if not self.stepper.move_robot(assets.ROBOT_DIRECTIONS.RIGHT, self.speed):
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
        transition = self.state_transitions.get((self.current_state, cs.get_color()))
        if transition is None:
            print(f"No transition found for state {self.current_state} and color {cs.get_color()}")
            self.execute_with_lock_and_notify(
                lambda: self.errors.append("Dein Turing Programm hat einen Reject State erreicht."))
            return False
        self.execute_with_lock_and_notify(
            lambda: setattr(self, 'current_state', transition['new_state']))
        toggle_retry = 0
        while cs.get_color() != transition['write_symbol']:
            if toggle_retry >= assets.TOGGLE_IO_BAND_RETRYS:
                self.execute_with_lock_and_notify(
                    lambda: self.errors.append("Das IO-Band kann nicht bearbeitet werden."))
                return False
            toggle_retry += 1
            self.stepper.toggle_io_band()
        if not self.stepper.move_robot(transition['move'], self.speed):
            self.execute_with_lock_and_notify(
                lambda: self.errors.append("Dein Turing Programm hat einen Reject State erreicht."))
            print("Band ended")
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
        self.home_robot()
        self.pause_machine()
        if self.should_stop:
            self.stop_by_flag()
            return False
        if not self.go_to_first_color():
            print("Blank io_band, Robot would move out of the LED strip")
            self.stepper.move_robot(assets.ROBOT_DIRECTIONS.LEFT, self.speed, 30)
        print("Robot reached the start of input")
        while self.current_state not in self.accept_states:
            self.pause_machine()
            if self.should_stop:
                self.stop_by_flag()
                return False
            print(f"Current state: {self.current_state}")
            if not self.single_step():
                print(self.errors)
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
