from __future__ import annotations
from person import Person, INFECTED, SUSCEPTIBLE, RECOVERED
import random

# Yo
class Graph:
    infected: set[Person]
    susceptible: set[Person]
    recovered = set[Person]

    def __init__(self) -> None:
        self.infected = set()
        self.susceptible = set()
        self.recovered = set()
        self.edges = set()

    def build_family_edge(self, person1: Person, person2: Person) -> None:
        person1.family.add(person2)
        person2.family.add(person1)

    def update_edge(self, current_frame, recover_period: int, close_contact_distance: int):
        print(len(self.infected))
        for patient in self.infected:
            patient.close_contact = {}
            if current_frame - patient.infection_frame > recover_period:
                patient.state = RECOVERED
                self.infected.remove(patient)
                self.recovered.add(patient)
            else:
                for person in self.susceptible:
                    if ((person.location[0] - patient.location[0]) ** 2 + (
                            person.location[1] - patient.location[1]) ** 2) ** 0.5 < close_contact_distance:
                        patient.create_close_contact_edge(person)

    def make_infection(self):
        '''return all the newly infected people'''
