from __future__ import annotations
from person_edge import Person, INFECTED, SUSCEPTIBLE, RECOVERED, Edge, CONTACT, FAMILY
import random

class Graph:
    infected: set[Person]
    susceptible: set[Person]
    recovered = set[Person]
    id_to_person: dict[int, Person]

    def __init__(self) -> None:
        self.infected = set()
        self.susceptible = set()
        self.recovered = set()
        self.id_to_person = {}
        self.edges = set()

    def build_family_edge(self, person1: Person, person2: Person) -> None:
        edge = Edge(person1, person2, FAMILY)
        person1.family[person2.id] = edge
        person2.family[person1.id] = edge

    def update_edge(self, current_frame, recover_period: int, close_contact_distance: int):
        to_remove = set()
        for patient in self.infected:
            patient.close_contact = {}
            print(patient.infection_frame)
            if current_frame - patient.infection_frame > recover_period:
                patient.state = RECOVERED
                to_remove.add(patient)
            else:
                for person in self.susceptible:
                    if ((person.location[0] - patient.location[0]) ** 2 + (
                            person.location[1] - patient.location[1]) ** 2) ** 0.5 < close_contact_distance:
                        patient.create_close_contact_edge(person)

        for patient in to_remove:
            self.infected.remove(patient)
            self.recovered.add(patient)

    def make_infection(self, close_contact_distance: int) -> set[Person]:
        """return all the newly infected people"""
        newly_infected = set()
        for patient in self.infected:
            for edge in patient.close_contact.values():
                if edge.infect(close_contact_distance) is not None:
                    newly_infected.add(edge.infect(close_contact_distance))
        return newly_infected
