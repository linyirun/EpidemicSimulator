from __future__ import annotations
import random
from typing import Optional

SUSCEPTIBLE = 1
INFECTED = 2
RECOVERED = 3
CONTACT = 9
FAMILY = 8


class Person:
    """
        Instance Attributes:
        - id:
            An unique identification of a person
        - family_id:
            An int idication the family the person belongs to
        - state:
            The state of a person that tells if he is infected, susceptable or rocovered.
        - location:
            The location interms of pixle of a person on the graph
        - move:
            How much interms of x and y a person will move in the next frame
        - close_contact:
            A dictionary contaning all the close contact perople with self. Key is the id of it's neighbors
            assciated
        - family:
            A dictionary contaning all the Person with the same family as self.
        - infection_frameL
            The frame that self is infected, this is None when self is not infected

        Representation Invariants:
        - not (self.state is INFECTED) or self.infection_frame is not None
        -
        """
    id: int
    family_id: int
    state: SUSCEPTIBLE | INFECTED | RECOVERED
    location: list[int, int]
    move: [int, int]
    moving_distance: float
    speed: float
    close_contact: dict[int: Edge]
    family: dict[int: Edge]
    infection_frame: Optional[int]  # the number of frame that this

    # initial location could be list of list as keeps list of moves [[0,0], [3,10]] initial should be starting point example 0,0
    def __init__(self, x: int, y: int, speed: float, family_id: int, id: int):
        """Status: 0 for susceptable, 1 for infected and 2 for recovered."""
        self.state = SUSCEPTIBLE
        self.family = {}
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
        self.close_contact[person.id] = Edge(self, person, CONTACT)


class Edge:
    person1: Person
    person2: Person
    relation: FAMILY | CONTACT

    def __init__(self, first: Person, second: Person, relation: FAMILY | CONTACT) -> None:
        self.person1 = first
        self.person2 = second
        self.relation = relation

    def infect(self, close_contact_distance: int) -> Optional[Person]:
        if (self.person1.state is INFECTED and self.person2 is not INFECTED) or (
                self.person1.state is not INFECTED and self.person2 is INFECTED):
            if self.relation is FAMILY:
                if random.random() < 0.05:
                    return self.get_infected_person()
                else:
                    return None
            else:
                distance = ((self.person1.location[0] - self.person2.location[0]) ** 2 + (
                        self.person1.location[1] - self.person2.location[1]) ** 2) ** 0.5
                factor = 0.001
                chance = 1 - ((close_contact_distance - distance) / close_contact_distance) ** 2 * factor
                if random.random() < chance:
                    return self.get_infected_person()
                else:
                    return None
        else:
            return None

    def get_infected_person(self):
        """
        - (self.person1.state is INFECTED and self.person2 is not INFECTED) or \
            (self.person1.state is not INFECTED and self.person2 is INFECTED)
        """
        if self.person1.state is INFECTED and self.person2 is not INFECTED:
            return self.person2
        else:
            return self.person1
