""" CSC111 PROJECT MAIN FILE: Virus Infection Simulation

GROUP MEMBERS: Richard Chen, Bill Lin, Runtong Liang, Yiyue Deng

This is the main runner file for our CSC111 project
"""
from __future__ import annotations
from typing import Optional
from collections import deque
import pygame as py
from simulation import Simulation as sim
import random
import math

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (95, 165, 228)

# Parameter Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 640
STATS_H, STATS_W = 200, 575
STACKED_GRAPH_LENGTH, STACKED_GRAPH_HEIGHT = 575, 225
NODE_RADIUS = 10
LINE_WIDTH = 1
TITLE = 'CSC111 Project'

# Pygame surface initialization
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = py.display.set_mode(size)
py.display.set_caption(TITLE)
stats = py.Surface((STATS_W, STATS_H))


class Button:
    """
    Creates a new pygame button

    Instance Attributes:
    - x: x position (based on pygame's coordinate system)
    - y: y position (based on pygame's coordinate system)
    - w: width
    - h: height
    - text: text to be displayed on button (if nothing put '')
    - text_color: text color in rgb stored in a tuple
    - background_color: the background color in rgb stored in a tuple
    - hover: true if one wants colour to change when mouse is over button, false if this colour change is unwanted
    - active: true if this button is active, false otherwise
    - rect: a pygame rect object of this button

    Representation Invariants:
    - SCREEN_WIDTH >= self.x >= 0 and SCREEN_HEIGHT >= self.y >= 0 and self.w <= SCREEN_WIDTH - self.x and self.h <= SCREEN_HEIGHT - self.y
    - not self.input_box or (self.text == '' or self.text.isdigit())
    """
    x: int
    y: int
    w: int
    h: int
    text: str
    text_color: tuple[int, int, int]
    background_color: tuple[int, int, int]
    hover: bool
    active: bool = False
    rect: py.Rect

    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 text_color: tuple[int, int, int],
                 background_c: tuple[int, int, int], hover: bool) -> None:
        """Initialize with the given information"""
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text
        self.text_color, self.background_color = text_color, background_c
        self.hover = hover
        self.rect = py.Rect(x, y, w, h)

    def update(self) -> None:
        """Redraw this button onto the main screen"""
        a, b = py.mouse.get_pos()
        comic_sans = py.font.SysFont('arial', 10)
        text_render = comic_sans.render(self.text, True, self.text_color)
        text_rect = text_render.get_rect(center=((self.w / 2) + self.x,
                                                 (self.h / 2) + self.y))
        background = py.Surface((self.w, self.h))
        if self.hover and self.x <= a <= self.x + self.w and self.y <= b <= self.y + self.h:
            background.fill(BLUE)
        else:
            background.fill(self.background_color)
        screen.blit(background, (self.x, self.y))
        screen.blit(text_render, text_rect)


class InputButton(Button):
    """
    A subclass of Button that only stores integer or float values
    The values of these buttons can be changed be the user

    Instance Attributes:
    - input_type: the type of input this button holds (float or int)
    - bounds: the bounds on the range of the input
    """
    input_type: str
    bounds: tuple[float | int, float | int]

    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 text_color: tuple[int, int,
                 int], background_c: tuple[int, int, int],
                 hover: bool, input_type: str, bounds: tuple[float | int,
                                                             float | int]):
        """Initialize with the given information"""
        super().__init__(x, y, w, h, text, text_color, background_c, hover)
        self.input_type = input_type
        self.bounds = bounds

    def update_text(self, event_unicode: str) -> None:
        """Update the text on this button only if the resulting text is valid
        Preconditons:
            - len(event_unicode) == 1
        """
        if self.input_type == 'float':
            # Checks if the resulting number is in the bound - otherwise make it empty
            to_add = event_unicode if self.bounds[0] <= float(self.text + event_unicode) <= \
                                      self.bounds[1] and len(self.text) < 5 else ''

            # Handling the input: If the text is just 0, make sure we don't add another integer after
            # Exception: "0." is a valid input
            if self.text != '0' or to_add == '.':
                self.text += to_add

        elif self.input_type == 'int':
            possible_text = self.text + event_unicode
            to_add = event_unicode if self.bounds[0] <= int(
                possible_text) < self.bounds[1] else ''
            self.text = str(int(self.text +
                                to_add)) if self.text + to_add != '' else ''


class StackedAreaGraph:
    """
    A class that contains the stacked area graph

    Private Instance Attributes:
    - _total_population: The total population in the current simulation
    - _data: The data for the frames up to the current time:
                     stores a tuple of (# uninfected, # infected, # recovered)
    - _graph: The graph in the simulation

    Representation Invariants:
        - all(sum(data) == total_population for data in self._data)
    """
    _total_population: int
    _data: deque[tuple[int, int, int]]
    _graph: Graph

    _infected_colour = (255, 0, 0)
    _cured_colour = (0, 0, 255)
    _uninfected_colour = (220, 220, 220)
    _stacked_graph_x = 600
    _stacked_graph_y = 300

    # TODO: Delete, for testing purposes
    _i = 0

    def __init__(self, total_population: int):
        # TODO: Implement this with graph: initialize the number of initial infected using the graph
        self._total_population = total_population
        # Initialize data to all uninfected
        self._data = deque([(total_population, 0, 0)] * STACKED_GRAPH_LENGTH)
        # self._graph = g

    def update(self):
        """Updates the graph for the current frame, then draw it

        """
        self._data.popleft()

        # new_frame = (0, self._total_population, 0)

        # TODO: This is for testing purposes
        new_frame = (self._total_population - self._i, self._i, 0)

        self._data.append(new_frame)

        # TODO: Delete, for testing purposes
        self._i += 1

        # Draw the graph onto the screen
        for i in range(len(self._data)):
            current_frame_data = self._data[i]
            percent_uninfected = current_frame_data[0] / self._total_population
            percent_infected = current_frame_data[1] / self._total_population
            percent_recovered = current_frame_data[2] / self._total_population

            height_uninfected = math.floor(percent_uninfected *
                                           STACKED_GRAPH_HEIGHT)
            height_infected = math.floor(percent_infected *
                                         STACKED_GRAPH_HEIGHT)
            height_recovered = math.floor(percent_recovered *
                                          STACKED_GRAPH_HEIGHT)

            while height_uninfected + height_infected + height_recovered < STACKED_GRAPH_HEIGHT:
                height_uninfected += 1

            self.draw_line_in_graph(
                (self._stacked_graph_x + i, self._stacked_graph_y),
                height_uninfected, self._uninfected_colour)
            self.draw_line_in_graph(
                (self._stacked_graph_x + i,
                 self._stacked_graph_y + height_uninfected), height_infected,
                self._infected_colour)
            self.draw_line_in_graph(
                (self._stacked_graph_x + i,
                 self._stacked_graph_y + height_uninfected + height_infected),
                height_recovered, self._cured_colour)

    def draw_line_in_graph(self, position: tuple[int, int], height: int,
                           color: tuple[int, int, int]) -> None:
        """Draws a line of width 1 at position, going down height pixels"""
        py.draw.line(screen, color, position,
                     (position[0], position[1] + height), 1)


def draw_node(position: tuple[int, int], colour: tuple[int, int, int]) -> None:
    """Draws a node at the given position

    Preconditions:
    - SCREEN_WIDTH >= position1[0] >= 0 and SCREEN_HEIGHT >= position1[1] >= 0
    """
    py.draw.circle(screen, colour, position, NODE_RADIUS)


def draw_edge(position1: tuple[int, int], position2: tuple[int, int], colour: tuple[int, int, int]) -> None:
    """Draws an edge between the two points

    Preconditions:
    - position1[0] >= 0 and position1[1] >= 0 and position2[0] >= 0 and position2[1] >= 0
    - position1[0] <= SCREEN_WIDTH and position1[1] <= SCREEN_HEIGHT
    - position2[0] <= SCREEN_WIDTH and position2[1] <= SCREEN_HEIGHT
    """
    py.draw.line(screen, colour, position1, position2, width=LINE_WIDTH)


def draw_text(x: int, y: int, text: str, font_size: int,
              font_color: tuple[int, int, int]):
    """draws text

    Preconditions:
    - SCREEN_HEIGHT >= x >= 0 and SCREEN_WIDTH >= y >= 0
    - text != ''
    - font_size > 0
    - len(font_color) == 3 and all(255 >= x >= 0 for x in font_color)
    """
    comic_sans = py.font.SysFont('arial', font_size)
    text_render = comic_sans.render(text, True, font_color)
    screen.blit(text_render, (x, y))


def update_text_and_graphs() -> None:
    """Updates all GUI elements except buttons (TO BE FINISHED)"""
    main_block = py.Rect(25, 25, 500, 500)
    py.draw.rect(screen, SKY_BLUE, main_block, 1)
    second_block = py.Rect(600, 300, STACKED_GRAPH_LENGTH,
                           STACKED_GRAPH_HEIGHT)
    py.draw.rect(screen, SKY_BLUE, second_block, 1)
    stats.fill(SKY_BLUE)
    screen.blit(stats, (600, 25))
    draw_text(120, 580, 'FAMILY SIZE', 15, WHITE)
    draw_text(140, 530, 'FAMILIES', 15, WHITE)
    draw_text(345, 580, 'INFECTIVITY', 15, WHITE)
    draw_text(310, 530, 'INITIAL INFECTED', 15, WHITE)


def main():
    """The function that runs the project"""
    # Initializes pygame stuff
    py.init()
    py.font.init()
    # Initializes buttons
    run_b = Button(25, 530, 70, 25, 'RUN', WHITE, RED, True)
    fam_pop_b = InputButton(215, 580, 60, 25, '100', BLACK, WHITE, True, 'int',
                            (1, 1000))
    regen_b = Button(25, 600, 70, 25, 'REGENERATE', WHITE, RED, True)
    fam_b = InputButton(215, 530, 60, 25, '2', BLACK, WHITE, True, 'int',
                        (1, 1000))
    infect_b = InputButton(445, 580, 60, 25, '0.5', BLACK, WHITE, True,
                           'float', (0.0, 1.0))
    inital_infected_b = InputButton(445, 530, 60, 25, '1', BLACK, WHITE, True,
                                    'int',
                                    (1, int(fam_pop_b.text) * int(fam_b.text)))

    stop_b = Button(25, 565, 70, 25, 'STOP', WHITE, RED, True)

    # Local variables
    # this button list is needed for the event tracking
    buttons = [
        run_b, fam_pop_b, fam_b, infect_b, regen_b, inital_infected_b, stop_b
    ]
    # Holds the currently active button
    active_button = None

    temp_population = 600
    # TODO: Implement this using the what the user inputs
    stacked_graph = StackedAreaGraph(temp_population)
    simulation = sim(5, 10, 5, 100, 10)
    simulation.frame()
    main_graph = simulation.simu_graph

    done = False
    clock = py.time.Clock()

    while not done:
        for event in py.event.get():
            # exit window
            if event.type == py.QUIT:
                done = True
            if event.type == py.MOUSEBUTTONDOWN:
                if active_button is not None:
                    active_button.active = False
                    active_button = None
                for b in buttons:
                    if b.rect.collidepoint(event.pos):
                        b.active = True
                        active_button = b
                        break
            if event.type == py.KEYDOWN and active_button is not None:
                if event.key == py.K_BACKSPACE:
                    # may need more functionality later
                    if isinstance(active_button, InputButton):
                        active_button.text = active_button.text[:-1]
                # takes care of integer input boxes
                elif isinstance(
                        active_button,
                        InputButton) and active_button.input_type == 'int':
                    try:
                        int(event.unicode)
                    except ValueError:
                        print('Not a valid integer')
                    else:
                        active_button.update_text(event.unicode)
                # takes care of floating point input boxes
                elif isinstance(active_button, InputButton):
                    # stores the current button's text plus what the user just inputted
                    possible_text = active_button.text + event.unicode
                    try:
                        float(possible_text)
                    except ValueError:
                        print('Not a valid floating point number')
                    else:
                        active_button.update_text(event.unicode)

        screen.fill(BLACK)
        # updates buttons
        for b in buttons:
            # updates bounds for initial infected
            if b is inital_infected_b:
                b.bounds = (1, int(fam_pop_b.text) * int(fam_b.text) if
                fam_pop_b.text != '' and fam_b.text != '' else 1)
                if b.text != '':
                    b.text = str(
                        min(
                            int(b.text),
                            int(fam_pop_b.text) * int(fam_b.text) if
                            fam_pop_b.text != '' and fam_b.text != '' else 1))
            b.update()

        # update main graph edges
        for i in main_graph.susceptible:
            for p in i.close_contact:
                x = main_graph.id_to_person[p].location[0]
                y = main_graph.id_to_person[p].location[1]
                draw_edge((i.location[0] + 25, i.location[1] + 25), (x + 25, y + 25), WHITE)
        for j in main_graph.infected:
            for m in j.close_contact:
                x = main_graph.id_to_person[m].location[0]
                y = main_graph.id_to_person[m].location[1]
                draw_edge((j.location[0] + 25, j.location[1] + 25), (x + 25, y + 25), WHITE)
        for k in main_graph.susceptible:
            for n in k.close_contact:
                x = main_graph.id_to_person[n].location[0]
                y = main_graph.id_to_person[n].location[1]
                draw_edge((k.location[0] + 25, k.location[1] + 25), (x + 25, y + 25), WHITE)
        # Update the main graph nodes
        for i in main_graph.susceptible:
            x = i.location[0]
            y = i.location[1]
            draw_node((x + 25, y + 25), (220, 220, 220))
        for j in main_graph.infected:
            x = j.location[0]
            y = j.location[1]
            draw_node((x + 25, y + 25), (255, 0, 0))
        for k in main_graph.recovered:
            x = k.location[0]
            y = k.location[1]
            draw_node((x + 25, y + 25), (0, 0, 255))

        update_text_and_graphs()

        stacked_graph.update()

        # nodes = []
        # NODES = 50
        # for i in range(NODES):
        #     node1 = (random.randint(25, 525), random.randint(25, 525))
        #     nodes.append(node1)
        #     draw_node(node1)
        #
        # for i in range(NODES - 1):
        #     for j in range(i + 1, NODES):
        #         draw_edge(nodes[i], nodes[j])

        py.display.flip()
        clock.tick(24)

    py.quit()


if __name__ == "__main__":
    main()
