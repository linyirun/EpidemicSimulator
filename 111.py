from __future__ import annotations
import random
from typing import Optional
from edge import Edge

SUSCEPTIBLE = 1
INFECTED = 2
RECOVERED = 3


class Person:
    id: int
    family_id: int
    state: SUSCEPTIBLE | INFECTED | RECOVERED
    location: list[int, int]
    last_move: [int, int]
    speed: float
    close_contact: dict[int: Edge]
    family: dict[int: Edge]
    infection_frame: Optional[int]  # the number of frame that this
    frames_per_second: float

    # initial location could be list of list as keeps list of moves [[0,0], [3,10]] initial should be starting point example 0,0
    def __init__(self, x: int, y: int, speed: float, family_id: int):
        """Status: 0 for susceptable, 1 for infected and 2 for recovered."""
        self.state = SUSCEPTIBLE
        self.family = {}
        self.family_id = family_id
        self.location = [x, y]
        self.speed = speed
        self.last_move = [0, 0]
        self.close_contact = {}
        self.infection_frame = Optional[int]
        self.frames_per_second = 24

    def make_move(self) -> None:
        """Makes random moves for person in a Brownian motion by updating location"""
        if self.infection_frame == 0:
            self.infection_frame = 1
        else:
            self.infection_frame += 1

            # Only move once per frame
        if self.infection_frame % self.frames_per_second != 0:
            return

        x, y = self.location
        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        distance_moved = self.speed / self.frames_per_second
        last_dx, last_dy = dx * distance_moved, dy * distance_moved
        x += last_dx
        y += last_dy
        # Make the person bounce off the borders
        if x < 0:
            x = -x
        elif x > 500:
            x = 1000 - x
        if y < 0:
            y = -y
        elif y > 500:
            y = 1000 - y
        self.last_move = [last_dx, last_dy]
        self.location = [int(x), int(y)]

    def create_close_contact_edge(self, person: Person):
        """
        person.state is SUSCEPTIBLE
        """
        self.close_contact[person.id] = Edge(self, person, CONTACT)
