from __future__ import annotations
import random
from typing import Optional
SUSCEPTIBLE = 1
INFECTED = 2
RECOVERED = 3

class Person:
    id: int
    family_id: int
    state: SUSCEPTIBLE | INFECTED | RECOVERED
    location: list[int, int]
    move: [int, int]
    moving_distance: float
    speed: float
    close_contact: dict[int: Edge]
    family: dict[int: Edge]
    infection_frame: Optional[int] # the number of frame that this

    # initial location could be list of list as keeps list of moves [[0,0], [3,10]] initial should be starting point example 0,0
    def __init__(self, x: int, y: int, speed: float, family_id: int, id: int):
        """Status: 0 for susceptable, 1 for infected and 2 for recovered."""
        self.state = SUSCEPTIBLE
        self.family = set()
        self.family_id = family_id
        self.location = [x, y]
        self.speed = speed
        self.move = [0, 0]
        self.close_contact = {}
        self.infection_frame = None
        self.id = id

    def make_move(self, time_elapsed: float) -> None:
        """Makes random moves for person in a Brownian motion by updating location"""
        x, y = self.location
        dx, dy = random.uniform(-self.moving_distance, self.moving_distance), random.uniform(-self.moving_distance,
                                                                                             self.moving_distance)
        elapsed_seconds = time_elapsed / 10  # divide by speed of 10 frames per second
        distance_moved = elapsed_seconds * self.speed
        x += dx * distance_moved
        y += dy * distance_moved
        # Make the person bounce off the borders
        if x < 0:
            x = -x
        elif x > 500:
            x = 1000 - x
        if y < 0:
            y = -y
        elif y > 500:
            y = 1000 - y
        self.location = [int(x), int(y)]
        # self.last_move_time = time.time()

    def create_close_contact_edge(self, person: Person):
        """
        person.state is SUSCEPTIBLE
        """
        self.close_contact[person.id] = Edge(self, person)


class Edge:
    person1: Person
    person2: Person

    def __init__(self, first: Person, second: Person) -> None:
        self.person1 = first
        self.person2 = second

    # def infect(self) -> None:
