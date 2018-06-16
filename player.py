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
                x = clickEvent['x']
                y = clickEvent['y']
                lag = self.calculate_lag(x, y)
                delay = self.calculate_delay(clickEvent['delay'], lag)
                self.sleep(delay)

                print(f'Slept for {delay+lag} now clicking at {x}, {y} with lag {lag}')

                time_since_first_click = self.prevent_premeture_alch(first, time_since_first_click)
                self.click(x, y, lag)
                first = not first
                self.last_x, self.last_y = x, y

    def prevent_premeture_alch(self, first, time_since_first_click):
        if not first:
            alch_time = datetime.now() - time_since_first_click
            if alch_time < timedelta(seconds=3.1):
                print(f'Preventing premature alch with sleep {alch_time.total_seconds()}')
                time.sleep(3.1 - alch_time.total_seconds())
            delta = alch_time
            print(f'Time per alch {delta.total_seconds()}')
            return datetime.now()
        else:
            return time_since_first_click

    def calculate_delay(self, delay, lag):
        if delay > 0:
            delay = delay / 1000000000
        delay = delay - lag if lag < delay else delay
        return delay if delay > 0.2 else delay + randint(20,30)/100 # Set minimum delay (adding 0.2-0.3)

    def calculate_lag(self, x, y):
        if self.last_x == x and self.last_y == y:
            return 0
        else:
            return randint(0, 10) / 10

    def sleep(self, delay):
            print(f'Sleeping for {delay}')
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