import numpy as np

class AvoidanceLogic:

    FORWARD = "FORWARD"
    TURN = "TURN"
    REVERSE = "REVERSE"

    AGGRESSIVE = "AGGRESSIVE"
    CAUTIOUS = "CAUTIOUS"
    STOP = "STOP"

    def __init__(self, forward_threshold=0.5, clear=1.0, turn=0.4):
        self.forward_threshold = forward_threshold
        self.clear_threshold = clear
        self.turn_threshold = turn
        self.state = self.FORWARD
        self.mode = self.CAUTIOUS

    def process_scan_data(self, msg):
        front_val = list([min(msg.ranges[0:15]), min(msg.ranges[-15:])])
        left_val = list([min(msg.ranges[75:105])])
        right_val = list([min(msg.ranges[-105:-75])])

        front_valid = [x for x in front_val if np.isfinite(x)]
        left_valid = [x for x in left_val if np.isfinite(x)]
        right_valid = [x for x in right_val if np.isfinite(x)]

        front = min(front_valid) if front_valid else float('inf')
        left = min(left_valid) if left_valid else float('inf')
        right = min(right_valid) if right_valid else float('inf')
        return front, left, right

    def decide_action(self, front, left, right):
        if front < self.forward_threshold and left < self.turn_threshold and right < self.turn_threshold:
            self.state = self.REVERSE
        elif front < self.forward_threshold and (left >= self.turn_threshold or right >= self.turn_threshold):
            self.state = self.TURN
        elif self.state == self.TURN and front >= self.clear_threshold:
            self.state = self.FORWARD
        elif self.state == self.REVERSE and front >= self.clear_threshold:
            self.state = self.FORWARD
        else:
            self.state = self.FORWARD
        return self.state

    def direction(self, left, right):
        if self.state == self.TURN:
            if left > right:
                return "LEFT"
            else:
                return "RIGHT"
        return None

    def get_speed(self):
        if self.mode == self.AGGRESSIVE:
            return 0.5
        elif self.mode == self.CAUTIOUS:
            return 0.2
        elif self.mode == self.STOP:
            return 0.0