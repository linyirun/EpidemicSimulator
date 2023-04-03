"""
This file contains the simulation.
"""
from __future__ import annotations
import random
# from python_ta.contracts import check_contracts
from graph import Graph
from person_edge import Person, INFECTED

NODE_RADIUS = 10


# @check_contracts
class Simulation:
    """A class represent one backend Simulation
    Instance Attributes:
        - simu_graph: the main graph in this simulation
        - close_contact_distance: the distance that the two person in this edge will be considered close contact
        interms of pixles
        - num_family: number of family in this silulation
        - family_size: number of Person in one family
        - frame_num: this records the number of frame that have passed in this simulation
        - infected: this is a set of people that should be infected in the next frame.
        - recover_period: after recover_period number of frames a person will recover in this simulation
        - brownian: If True, people in this simulation move in brownian motions otherwise they randomly move and
        bounce back when hit a wall.
        - id_to_family: This is a dictionary with id of a family associated with list of all the person in that family
        - fps: frames per second in this simulation

    Representation Invarients:
        - all(all(person.family_id == family for person in self.id_to_family[family]) for family in self.id_to_family)
        - frame_num >= 0
        - len(infected) <= self.num_family*self.family_size

    """
    simu_graph: Graph
    close_contact_distance: int  # in pixles
    num_family: int
    family_size: int
    frame_num: int
    infected: set
    recover_period: int  # in frames
    brownian: bool
    id_to_family: dict[int, list[Person]]
    fps: int

    def __init__(self, num_family: int, family_size: int, speed: int, recover_period: int, initial_infected: int,
                 close_contact_distance: int, fps: int, infectivity: float, brownian: bool = False) -> None:
        """
        Initialize the simulation class
        Preconditions:
            - initial_infected <= num_family * family_size
        """
        self.recover_period = recover_period
        self.simu_graph = Graph(infectivity)
        self.infected = set()
        self.frame_num = 0
        self.num_family = num_family
        self.family_size = family_size
        self.close_contact_distance = close_contact_distance
        self.brownian = brownian
        self.fps = fps
        self.id_to_family = {}

        person_id = 0
        for i in range(1, num_family + 1):
            added = []
            # Create a clique between this family, and add each person in the family to the suspectible
            # set in the graph
            for _ in range(family_size):
                x = random.randint(NODE_RADIUS, 500 - NODE_RADIUS)
                y = random.randint(NODE_RADIUS, 500 - NODE_RADIUS)
                person = Person(x, y, speed, i, person_id, fps)
                person_id += 1
                for one in added:
                    self.simu_graph.build_family_edge(one, person)
                added.append(person)
                self.simu_graph.susceptible.add(person)
                self.simu_graph.id_to_person[person.id] = person
            self.id_to_family[i] = added

        # Randomly choose initial_infected number of people to be infected
        for _ in range(initial_infected):
            to_infect = self.simu_graph.susceptible.pop()
            to_infect.infection_frame = 0
            self.simu_graph.infected.add(to_infect)
            to_infect.state = INFECTED

    def frame(self) -> None:
        """This fuction update the graph for the next frame. This update incudes the location of all the Person,
        the close contact edges, and the states of each Person.
        """
        self.frame_num += 1
        # move
        for person in self.simu_graph.infected | self.simu_graph.susceptible | self.simu_graph.recovered:
            if self.brownian:
                person.make_move_brownian()
            else:
                person.make_move_person()
        # infect
        # has_none = False
        for person in self.infected:
            # print(self.simu_graph.make_infection(self.close_contact_distance))
            person.state = INFECTED
            person.infection_frame = self.frame_num
            self.simu_graph.susceptible.remove(person)
            self.simu_graph.infected.add(person)
        self.simu_graph.update_edge(self.frame_num, self.recover_period, self.close_contact_distance)

        self.infected = self.simu_graph.make_infection(self.close_contact_distance)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'disable': ['E9999', 'R0902', 'R0913', 'R0914'],
        'max-line-length': 120
    })
