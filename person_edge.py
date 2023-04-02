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
            An unique identification of a person.
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
        - 0 <= self.location[0] <= 500 and 0 <= self.location[1] <= 500
        """
    id: int
    family_id: int
    state: SUSCEPTIBLE | INFECTED | RECOVERED
    location: list[int, int]
    move: [int, int]
    speed: float
    close_contact: dict[int: Edge]
    family: dict[int: Edge]

    # initial location could be list of list as keeps list of moves [[0,0], [3,10]] initial should be starting point example 0,0
    def __init__(self, x: int, y: int, speed: int, family_id: int, id: int, fps: int):
        """Status: 0 for susceptable, 1 for infected and 2 for recovered.

        Preconditions:
        - speed >= 1
        """
        self.state = SUSCEPTIBLE
        self.family = {}
        self.family_id = family_id
        self.location = [x, y]
        self.speed = speed
        self.close_contact = {}
        self.infection_frame = Optional[int]
        self.id = id
        moving_value = speed / 2**0.5
        direction = [-1, 1]
        self.move = [int(random.choice(direction)*moving_value), int(random.choice(direction)*moving_value)]
        self.speed = speed * fps
        self.frames_per_second = fps

    def make_move_brownian(self) -> None:
        """Makes random moves for person in a Brownian motion by updating location"""
        x, y = self.location
        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        magnitude = (dx ** 2 + dy ** 2) ** 0.5  # magnitude of movement vector
        if magnitude == 0:
            dx, dy = dx / magnitude, dy / magnitude  # normalize the vector to a unit vector
        distance_moved = self.speed / self.frames_per_second
        dx, dy = dx * distance_moved, dy * distance_moved  # multiply by distance moved
        x += dx
        y += dy
        # Make the person bounce off the borders
        if x < 10:
            x = 10 + (10 - x)
        elif x > 490:
            x = 980 - x
        if y < 10:
            y = 10 + (10 - y)
        elif y > 490:
            y = 980 - y
        self.last_move = [dx, dy]
        self.location = [x, y]
        # self.last_move_time = time.time()

    def make_move_person(self):
        next_x = self.location[0] + self.move[0]
        next_y = self.location[1] + self.move[1]
        if next_x > 490:
            self.move[0] = -self.move[0]
            next_x = 490 - (next_x - 490)
        if next_x < 10:
            self.move[0] = -self.move[0]
            next_x = 10 + (10 - next_x)
        if next_y > 490:
            self.move[1] = -self.move[1]
            next_y = 490 - (next_y - 490)
        if next_y < 10:
            self.move[1] = -self.move[1]
            next_y = 10 + (10 - next_y)
        self.location[0], self.location[1] = next_x, next_y

    def create_close_contact_edge(self, person: Person):
        """
        - person.state == SUSCEPTIBLE
        """
        self.close_contact[person.id] = Edge(self, person)


class Edge:
    person1: Person
    person2: Person

    def __init__(self, first: Person, second: Person) -> None:
        self.person1 = first
        self.person2 = second

    def infect(self, close_contact_distance: int) -> Optional[Person]:
        if (self.person1.state is INFECTED and self.person2 is not INFECTED) or (
            self.person1.state is not INFECTED and self.person2 is INFECTED):
            # Separate check for people in the same family
            if self.person1.family_id == self.person2.family_id:
                if random.random() < 1:
                    return self.get_infected_person()
                else:
                    return None
            else:
                distance = ((self.person1.location[0] - self.person2.location[0]) ** 2 + (
                        self.person1.location[1] - self.person2.location[1]) ** 2) ** 0.5
                factor = 0.5
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

def test_make_move():
    person = Person(250, 250, 8, 1, 1)
    while True:
        print(person.location)
        person.make_move()
