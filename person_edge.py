"""
This file contains both the person and the edge class
"""

from __future__ import annotations
import random
from typing import Optional
# from python_ta.contracts import check_contracts

SUSCEPTIBLE = 1
INFECTED = 2
RECOVERED = 3
CONTACT = 9
FAMILY = 8


# @check_contracts
class Person:
    """This class is a representation of a person in the square or a node in the graph.

        Instance Attributes:
        - id: An unique identification of a person.
        - family_id: An int idication the family the person belongs to
        - state: The state of a person that tells if he is infected, susceptable or rocovered.
        - location: The location interms of pixle of a person on the graph
        - move: How much interms of x and y a person will move in the next frame
        - close_contact: A dictionary contaning all the close contact perople with self. Key is the id of it's neighbors
        assciated
        - family: A dictionary contaning all the Person with the same family as self.
        - infection_frame: The frame that self is infected, this is None when self is not infected
        - frames_per_second: The frames/sec for the simulation
        - last_move: The last move made by the person, used for Brownian motion

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
    infection_frame: Optional[int]
    frames_per_second: int
    last_move: list[float, float]

    def __init__(self, x: int, y: int, speed: int, family_id: int, identification: int, fps: int) -> None:
        """Initialize a person. Status: 0 for susceptable, 1 for infected and 2 for recovered.

        Preconditions:
        - speed >= 1
        """
        self.state = SUSCEPTIBLE
        self.family = {}
        self.family_id = family_id
        self.location = [x, y]
        self.speed = speed
        self.close_contact = {}
        self.infection_frame = None
        self.id = identification
        moving_value = speed / 2 ** 0.5
        direction = [-1, 1]
        self.move = [int(random.choice(direction) * moving_value), int(random.choice(direction) * moving_value)]
        self.speed = speed * fps
        self.frames_per_second = fps

    def make_move_brownian(self) -> None:
        """Makes random moves for person in a Brownian motion by updating location"""
        x, y = self.location
        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        magnitude = (dx ** 2 + dy ** 2) ** 0.5  # magnitude of movement vector
        if magnitude != 0:
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

    def make_move_person(self) -> None:
        """More the person to location of the next frame and bounce back when the person hits the wall.
        """
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

    def create_close_contact_edge(self, person: Person) -> None:
        """Creat a close contact edge between two person.

        Precondation:
        - person.state == SUSCEPTIBLE or self.state == SUSCEPTIBLE
        """
        self.close_contact[person.id] = Edge(self, person)
        person.close_contact[self.id] = Edge(person, self)


class Edge:
    """This class represent an edge between two people either a family edge or a close ocntact edge depend on the
    family edge of person

    - Representation Invariants:
        self.person1 is not None and self.person2 is not None
    """
    person1: Person
    person2: Person

    def __init__(self, first: Person, second: Person) -> None:
        """This inicialize an edge between the given two person.

        Instance Attributes:
            - person1: a person in the edge
            - person2: a person in the edge

        - Preconditions:
            - first is not None and second is not None

        """
        self.person1 = first
        self.person2 = second

    def infect(self, close_contact_distance: int, infectivity: float) -> Optional[Person]:
        """ This function have a chance of retuning a person who should be infected in self if one gets infected.
        This function will not return a person if none of the two person in self are infected. The chances of infection
        depend on if the two person are in the same family or if they are close contact.
        If they are in the family there is a concrete chance that one will infect another.
        If they are close contacts, the change of infection will grow exponancially as the two person are
        getting closer.

        - Preconditions:
            - close_contact_distance > 0
        """
        if (self.person1.state == INFECTED and self.person2.state == SUSCEPTIBLE) or (
                self.person1.state == SUSCEPTIBLE and self.person2.state == INFECTED):
            # Separate check for people in the same family
            if self.person1.family_id == self.person2.family_id:
                if random.random() <= infectivity / 100:
                    return self.get_infected_person()
                else:
                    return None
            else:
                distance = ((self.person1.location[0] - self.person2.location[0]) ** 2 + (
                            self.person1.location[1] - self.person2.location[1]) ** 2) ** 0.5
                chance = infectivity - ((close_contact_distance - distance) / close_contact_distance) ** 2
                if random.random() < chance:
                    return self.get_infected_person()
                else:
                    return None
        else:
            return None

    def get_infected_person(self) -> Person:
        """ This function returns the person who is infected.
        Preconditions:
        - (self.person1.state is INFECTED and self.person2 is not INFECTED) or \
            (self.person1.state is not INFECTED and self.person2 is INFECTED)
        """
        if self.person1.state is INFECTED and self.person2 is not INFECTED:
            return self.person2
        else:
            return self.person1


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'disable': ['E9999', 'R0902', 'R0913'],
        'max-line-length': 120
    })
