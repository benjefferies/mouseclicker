# -*- coding: utf-8 -*-
import argparse
import json
import time
import timeit
from collections import OrderedDict
from datetime import timedelta, datetime
from random import randint

import pyautogui


def make_parser():
    parser = argparse.ArgumentParser(description="Play logged clicks.")
    parser.add_argument('file', action="store", help="Name file with recordings")
    parser.add_argument('runtime', action="store", help="Runtime of clicker in minutes")
    return parser


class Clicker(object):

    def __init__(self, clickFile, runtime) -> None:
        with open(clickFile) as file:
            contents = file.read()
            self.batched_clicks = json.loads(contents, object_pairs_hook=OrderedDict)
            self.runtime = int(runtime)
            self.start_time = datetime.now()
            self.last_x, self.last_y = None, None

    def start(self):
        while self.running_time() < timedelta(minutes=self.runtime):
            first = True
            time_since_first_click = datetime.now()
            for clickEvent in self.get_random_batch():
                if first:
                    time_since_first_click = datetime.now()
                x, y = clickEvent['x'], clickEvent['y']
                mouse_move_duration = self.calculate_lag(x, y)
                delay = self.calculate_delay(clickEvent['delay'], mouse_move_duration)
                predicted_time_per_alch = datetime.now() + timedelta(seconds=delay) - time_since_first_click
                additional_delay = self.prevent_premeture_alch(predicted_time_per_alch, first)
                delay += additional_delay
                predicted_time_per_alch += timedelta(seconds=additional_delay)
                self.sleep(delay)
                print(f'Slept for {delay} + {mouse_move_duration} mouse delay now clicking at {x}, {y}')
                if not first:
                    print(f'Time per alch {predicted_time_per_alch.total_seconds()}')
                self.click(x, y, mouse_move_duration)
                first = not first
                self.last_x, self.last_y = x, y

    def prevent_premeture_alch(self, time_per_alch, first):
            if not first and time_per_alch < timedelta(seconds=3.1):
                print(f'Preventing premature alch by adding delay {time_per_alch.total_seconds()}')
                return 3.1 + randint(100, 300)/1000 - time_per_alch.total_seconds()
            else:
                return 0

    def calculate_delay(self, delay, mouse_move_duration):
        if delay > 0:
            delay = delay / 1000000000
        delay = delay - mouse_move_duration if mouse_move_duration < delay else delay
        return delay if delay > 0.2 else delay + randint(20,30)/100 # Set minimum delay (adding 0.2-0.3)

    def calculate_lag(self, x, y):
        if self.last_x == x and self.last_y == y:
            return 0
        else:
            return randint(0, 10) / 10

    def sleep(self, delay):
        time.sleep(delay)

    def get_random_batch(self):
        return self.batched_clicks[randint(0, len(self.batched_clicks) - 1)]

    def click(self, x, y, lag):
        pyautogui.click(x, y, button="left", duration=lag)

    def running_time(self):
        return datetime.now() - self.start_time

if __name__ == '__main__':
    args = make_parser().parse_args()

    clicker = Clicker(args.file, args.runtime)
    print(f'Starting clicker with {args.file} and runtime of {args.runtime}')
    print("Press enter to start clicking.")
    input()
    print("Clicking starts in 3 seconds.")
    time.sleep(3.0)
    clicker.start()