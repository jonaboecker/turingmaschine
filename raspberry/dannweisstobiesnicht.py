"""
This module contains the state machine to control the robot.
"""

# pylint: todo: disable=fixme

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


    def home_robot(self):
        """Homing the robot"""
        # todo: improve the homing
        while not lb.get_state():
            self.stepper.move_robot(assets.ROBOT_DIRECTIONS.LEFT, self.speed)
        print("Robot homed")

    def go_to_first_color(self):
        """
        Moving the robot to the first color
        Returns:
            bool: True if the robot reached the first color,
                  False if the robot would move out of the LED strip.
        """
        while cs.get_color() == assets.IO_BAND_COLORS.BLANK:
            if not self.stepper.move_robot(assets.ROBOT_DIRECTIONS.RIGHT, self.speed):
                return False
        return True

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
            self.errors.append("Dein Turing Programm hat einen Reject State erreicht.")
            return False
        self.current_state = transition['new_state']
        toggle_retry = 0
        while cs.get_color() != transition['write_symbol']:
            if toggle_retry >= assets.TOGGLE_IO_BAND_RETRYS:
                self.errors.append("Das IO-Band kann nicht bearbeitet werden.")
                return False
            toggle_retry += 1
            self.stepper.toggle_io_band()
        if not self.stepper.move_robot(transition['move'], self.speed):
            self.errors.append("Dein Turing Programm ist zu groß für das IO-Band.")
            print("Band ended")
            return False
        self.steps += 1
        return True

    def run(self):
        """
        Run the state machine
        :returns:
            bool: True if the tm reached an accept state,
                  False if there accept wasn't reached, reason is saved in self.errors.
        """
        self.running = True
        self.home_robot()
        if not self.go_to_first_color():
            print("Blank io_band, Robot would move out of the LED strip")
            self.stepper.move_robot(assets.ROBOT_DIRECTIONS.LEFT, self.speed, 30)
        print("Robot reached the start of input")
        while self.current_state not in self.accept_states:
            print(f"Current state: {self.current_state}")
            if not self.single_step():
                print(self.errors)
                return False
        print("Robot reached an accept state")
        self.running = False
        return True
