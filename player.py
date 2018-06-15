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

def sleep(delay):
    if delay > 0:
        delay_in_seconds = delay / 1000000000
        print(f'Sleeping for {delay_in_seconds}')
        time.sleep(delay_in_seconds)

class Clicker(object):

    def __init__(self, clickFile, runtime) -> None:
        with open(clickFile) as file:
            contents = file.read()
            self.batched_clicks = json.loads(contents, object_pairs_hook=OrderedDict)
            self.runtime = int(runtime)
            self.start_time = datetime.now()

    def start(self):
        while self.running_time() < timedelta(minutes=self.runtime):
            first = True
            time_since_first_click = datetime.now()
            for clickEvent in self.get_random_batch():
                delay = clickEvent['delay']
                actually_took = timeit.timeit(f'player.sleep({delay})', setup='import player', number=1)

                x = clickEvent['x']
                y = clickEvent['y']
                print(f'Wanted to sleep for {delay} actually slept for {actually_took/10000000} now clicking at {x}, {y}')
                self.click(x, y)
                if not first:
                    delta = datetime.now() - time_since_first_click
                    print(f'Time per alch {delta.total_seconds()}')
                    time_since_first_click = datetime.now()
                first = not first

    def get_random_batch(self):
        return self.batched_clicks[randint(0, len(self.batched_clicks) - 1)]

    def click(self, x, y):
        pyautogui.click(x, y, button="left", duration=randint(0,10)/10)

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