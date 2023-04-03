""" FRONTEND FILE

This file contains all the code for the front end, as well as the Runner class that runs the entire
project by connecting the front end to the back end
"""
from __future__ import annotations
from typing import Optional
from collections import deque
import math
import pygame as py
import pygame.event
from python_ta.contracts import check_contracts
from simulation import Simulation as sim
from person_edge import INFECTED, SUSCEPTIBLE, RECOVERED
from graph import Graph

# Colours
BLACK = (0, 0, 0)
# Edge Colour
WHITE = (255, 255, 255)
# Infected Colour
RED = (255, 0, 0)
# Node Colours (20 of them, 1 per family)
SKY_BLUE = (95, 165, 228)
GREEN = (0, 255, 0)
COLORS = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (192, 192, 192), (128, 128, 128),
          (128, 0, 0), (128, 128, 0), (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (205, 133, 63),
          (255, 250, 240), (230, 230, 250), (123, 104, 238), (100, 149, 237), (175, 238, 238), (95, 165, 228)]

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

# global non constant variables
button_changed = True


@check_contracts
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
    - SCREEN_WIDTH >= self.x >= 0 and SCREEN_HEIGHT >= self.y >= 0
    - self.w <= SCREEN_WIDTH - self.x and self.h <= SCREEN_HEIGHT - self.y
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
            background.fill(SKY_BLUE)
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

    Representation Invariants:
    - input_type == 'float' or input_type == 'int'
    """
    input_type: str
    bounds: tuple[float | int, float | int]

    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 text_color: tuple[int, int, int], background_c: tuple[int, int, int],
                 hover: bool, input_type: str, bounds: tuple[float | int, float | int]) -> None:
        """Initialize with the given information"""
        super().__init__(x, y, w, h, text, text_color, background_c, hover)
        self.input_type = input_type
        self.bounds = bounds

    def update_text(self, event_unicode: str) -> None:
        """Update the text on this button only if the resulting text is valid
        Preconditons:
            - len(event_unicode) == 1
        """
        global button_changed
        if self.input_type == 'float':
            # Checks if the resulting number is in the bound - otherwise make it empty
            to_add = event_unicode if self.bounds[0] <= float(self.text + event_unicode) <= self.bounds[1] and len(
                self.text) < 5 else ''

            # Handling the input: If the text is just 0, make sure we don't add another integer after
            # Exception: "0." is a valid input
            if (self.text != '0' or to_add == '.') and to_add != '':
                self.text += to_add
                button_changed = True

        elif self.input_type == 'int':
            possible_text = self.text + event_unicode
            if self.bounds[0] <= int(possible_text) < self.bounds[1]:
                to_add = event_unicode
                button_changed = True
            else:
                to_add = ''
            self.text = str(int(self.text + to_add)) if self.text + to_add != '' else ''

    def change_bound(self, new_bounds: tuple[int, int]) -> None:
        """Function to change the current bounds"""
        self.bounds = new_bounds


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

    _infected_colour: tuple[int, int, int] = (255, 0, 0)
    _cured_colour: tuple[int, int, int] = (0, 0, 255)
    _uninfected_colour: tuple[int, int, int] = (220, 220, 220)
    _stacked_graph_x: int = 600
    _stacked_graph_y: int = 300

    def __init__(self, total_population: int, g: Graph) -> None:
        self._total_population = total_population
        # Initialize data to all uninfected
        self._data = deque([(total_population, 0, 0)] * STACKED_GRAPH_LENGTH)
        self._graph = g

    def update(self, is_running: bool) -> None:
        """Updates the graph for the current frame, then draw it
        """

        # Only update if the simulation is currently running
        if is_running:
            self._data.popleft()

            # Calculate the data for the current frame, then add it
            uninfected = len(self._graph.susceptible)
            infected = len(self._graph.infected)
            recovered = len(self._graph.recovered)

            new_frame = (uninfected, infected, recovered)
            self._data.append(new_frame)

        # Draw the graph onto the screen
        for i in range(len(self._data)):
            current_frame_data = self._data[i]
            percent_uninfected = current_frame_data[0] / self._total_population
            percent_infected = current_frame_data[1] / self._total_population
            percent_recovered = current_frame_data[2] / self._total_population

            height_uninfected = math.floor(percent_uninfected * STACKED_GRAPH_HEIGHT)
            height_infected = math.floor(percent_infected * STACKED_GRAPH_HEIGHT)
            height_recovered = math.floor(percent_recovered * STACKED_GRAPH_HEIGHT)

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
        """Draws a line of width 1 at position, going down height pixels

        Preconditons:
        - height >= 0
        """
        py.draw.line(screen, color, position,
                     (position[0], position[1] + height), 1)


class StatsTable:
    """A class representing the stats table
    Displays 5 rows: first row is the header, the other rows will be the data for each family
    Displays 4 columns

    Instance Attributes:
    - data_table: stores the data for each family: it has num_families rows, and each row has 4 elements, indicating:
    [family id, # uninfected, # infected, # recovered]
    - num_families: the number of families in the current simulation
    - graph: the simulation graph
    - current_top_row: the index of the first row that we are displaying

    Representation Invariants:
    - 0 <= current_top_row <= self.num_families - 4
    """
    data_table: list[list[int, int, int, int]]
    num_families: int
    simulation: sim
    current_top_row: int

    pos_x: int = 600
    pos_y: int = 25
    line_color: tuple[int, int, int] = (222, 222, 222)
    border_line_width: int = 3

    _header_font_size: int = 25
    _text_font_size: int = 20

    def __init__(self, num_families: int, simulation: sim) -> None:
        """Initializes the stats table"""
        self.num_families = num_families
        self.current_top_row = 0
        self.simulation = simulation

        # Initialize the data table with num_families rows with 4 elements each row
        self.data_table = []
        for i in range(num_families):
            self.data_table.append([i, 0, 0, 0])

    def update(self) -> None:
        """Updates self by:
        Recalculating values for each family, then redrawing the table with updated values
        """
        # Calculate the values for each family
        for family_id in range(1, self.num_families + 1):
            uninfected = sum(1 for person in self.simulation.id_to_family[family_id] if person.state == SUSCEPTIBLE)
            infected = sum(1 for person in self.simulation.id_to_family[family_id] if person.state == INFECTED)
            recovered = sum(1 for person in self.simulation.id_to_family[family_id] if person.state == RECOVERED)
            self.data_table[family_id - 1] = [family_id, uninfected, infected, recovered]

        # Draw total table
        self.draw_total_table(6)
        # Drawing the table background
        stats.fill(SKY_BLUE)
        screen.blit(stats, (self.pos_x, self.pos_y))
        # Drawing header
        self.draw_center_text('Family ID', self._header_font_size, BLACK, 0, 0)
        self.draw_center_text('Uninfected', self._header_font_size, BLACK, 0, 1)
        self.draw_center_text('Infected', self._header_font_size, BLACK, 0, 2)
        self.draw_center_text('Recovered', self._header_font_size, BLACK, 0, 3)

        for i in range(min(len(self.data_table), 4)):
            for j in range(len(self.data_table[i])):
                self.draw_center_text(str(self.data_table[self.current_top_row + i][j]), self._text_font_size, BLACK,
                                      i + 1, j)

        # Drawing lines
        for i in range(0, 6):
            self.draw_line_in_table((self.pos_x, self.pos_y + STATS_H // 5 * i),
                                    (self.pos_x + STATS_W, self.pos_y + STATS_H // 5 * i))

        # Draw the vertical lines for the border
        for i in range(0, 4):
            self.draw_line_in_table((self.pos_x + STATS_W // 4 * i, self.pos_y),
                                    (self.pos_x + STATS_W // 4 * i, self.pos_y + STATS_H))
        # Draw the final vertical line
        self.draw_line_in_table((self.pos_x + STATS_W, self.pos_y),
                                (self.pos_x + STATS_W, self.pos_y + STATS_H))

    def draw_center_text(self, text: str, font_size: int, font_color: tuple[int, int, int], row: int, col: int) -> None:
        """Draws text in the center of a cell in the table

        Preconditons:
        - font_size >= 1
        - 0 <= row <= len(self.data_table)
        - 0 <= col <= len(self.data_table[0])
        """
        width_cell = STATS_W // 4
        height_cell = STATS_H // 5
        comic_sans = py.font.SysFont('arial', font_size)
        text_render = comic_sans.render(text, True, font_color)
        text_rect = text_render.get_rect(center=((width_cell / 2) + self.pos_x + col * width_cell,
                                                 (height_cell / 2) + self.pos_y + row * height_cell))
        screen.blit(text_render, text_rect)

    def draw_line_in_table(self, position: tuple[int, int], position2: tuple[int, int]) -> None:
        """Draws a line, starting from position to the end of the table

        Preconditons:
        - 0 <= position[0] <= SCREEN_WIDTH
        - 0 <= position[1] <= SCREEN_HEIGHT
        - 0 <= position2[0] <= SCREEN_HEIGHT
        - 0 <= position2[1] <= SCREEN_HEIGHT
        """
        # end_position = (position[0] + STATS_W, position[1])
        py.draw.line(screen, self.line_color, position, position2, width=self.border_line_width)

    def check_scroll(self, x: int, y: int, dy: int) -> None:
        """checks if we can scroll up or down
        If we can't, then clamp the top row so that we can see at 4 rows

        Preconditions:
        - 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT
        """
        if self.pos_x <= x <= self.pos_x + STATS_W and self.pos_y <= y <= self.pos_y + STATS_H:
            # clamps
            self.current_top_row = max(min(self.current_top_row + dy, self.num_families - 4), 0)

    def draw_total_table(self, border_radius: int) -> None:
        """Draws the row that displays the total stats, and the text that goes along with it

        Preconditions:
        - border_radius % 2 == 0
        """
        bigger_background = py.Surface((STATS_W, 40))
        bigger_background.fill((220, 220, 220))
        smaller_background = py.Surface((STATS_W - border_radius, 40 - border_radius))
        smaller_background.fill(SKY_BLUE)
        screen.blit(bigger_background, (self.pos_x, self.pos_y + STATS_H + 20))
        screen.blit(smaller_background,
                    (self.pos_x + border_radius // 2, self.pos_y + STATS_H + 20 + border_radius // 2))

        # Calculate the data for the current frame, then add it
        uninfected = len(self.simulation.simu_graph.susceptible)
        infected = len(self.simulation.simu_graph.infected)
        recovered = len(self.simulation.simu_graph.recovered)

        draw_text(self.pos_x + border_radius * 2, self.pos_y + STATS_H + 28, f"Uninfected: {uninfected}", 20, BLACK)
        draw_text(self.pos_x + border_radius * 2 + 215, self.pos_y + STATS_H + 28, f"Infected: {infected}", 20, BLACK)
        draw_text(self.pos_x + border_radius * 2 + 400, self.pos_y + STATS_H + 28, f"Recovered: {recovered}", 20, BLACK)


class Runner:
    """
    Runs the pygame display and simulation

    Instance Attributes:
    - buttons: a dictionary that maps a string name to the button
    - active_button: the active button that is selected
    - simulation: the current simulation in Runner
    - main_graph: the main graph on the left of the display that represents the simulation
    - stacked_graph: the graph on the right of the display that shows the proportion of node states over time
    - stats_table: the scrollable table that is displayed on the top right of the display
    - done: whether this Pygame window is done Running (only true if one presses exit)
    - is_running: whether the current simulation is currently running
    - can_initialize_run: whether is it legal for the simulation to start running
    - draw_run_error: whether the empty field error can be displayed
    - fps: the fps of the display
    - error_timer: the amount of frames that the run error message stays on the screen
    - clock: a pygame.time.Clock that updates Runner at fps frames per second
    - done_frames: a variables used to count frames after the simulation ends

    Representation Invariants:
    - 0 < self.fps <= 60
    - 0 < self.error_timer <= self.fps * 5
    """
    buttons: dict[str: Button]
    active_button: Optional[Button]
    simulation: Optional[sim]
    main_graph: Optional[Graph]
    stacked_graph: Optional[StackedAreaGraph]
    stats_table: Optional[StatsTable]
    done: bool = False
    is_running: bool = False
    can_initialize_run: bool = True
    draw_run_error: bool = False
    fps: int
    error_timer: int
    clock: py.time.Clock
    done_frames: int = 0

    def __init__(self, fps: int) -> None:
        """Initializes with the parameters

        Instance Attributes:

        """
        py.init()
        py.font.init()
        # Buttons are preset for this project
        run_b = Button(25, 530, 70, 25, 'RUN', WHITE, RED, True)
        fam_pop_b = InputButton(215, 580, 60, 25, '5', BLACK, WHITE, True, 'int', (1, 51))
        regen_b = Button(25, 600, 70, 25, 'REGENERATE', WHITE, RED, True)
        fam_b = InputButton(215, 530, 60, 25, '5', BLACK, WHITE, True, 'int', (1, 21))
        infect_b = InputButton(445, 580, 60, 25, '0.2', BLACK, WHITE, True, 'float', (0.0, 1.0))
        inital_infected_b = InputButton(445, 530, 60, 25, '1', BLACK, WHITE, True,
                                        'int', (1, int(fam_pop_b.text) * int(fam_b.text) + 1))
        stop_b = Button(25, 565, 70, 25, 'STOP', WHITE, RED, True)
        close_cont_b = InputButton(700, 530, 60, 25, '100', BLACK, WHITE, True, 'int', (1, 1000))
        speed_b = InputButton(700, 580, 60, 25, '5', BLACK, WHITE, True, 'int', (1, 21))
        recover_period = InputButton(940, 530, 60, 25, '3', BLACK, WHITE, True, 'float', (1, 10000))
        brownian = Button(940, 580, 25, 25, '', WHITE, RED, False)
        self.buttons = {
            'run': run_b, 'fam_pop': fam_pop_b, 'fam': fam_b, 'infect': infect_b, 'regen': regen_b,
            'initial': inital_infected_b, 'stop': stop_b, 'close': close_cont_b, 'speed': speed_b,
            'recover': recover_period,
            'brownian': brownian
        }
        self.active_button = None
        self.simulation = None
        self.main_graph = None
        self.stacked_graph = None
        self.stats_table = None
        self.fps = fps
        self.error_timer = fps
        self.clock = py.time.Clock()

    def run(self) -> None:
        """runs the Runner (the entire project)"""
        while not self.done:
            self.event_check()
            screen.fill(BLACK)
            self.update_buttons()
            self.update_data_objects()
            self.check_error_fields()
            if self.is_running:
                self.simulation.frame()
            self.draw_main_graph()
            self.stacked_graph.update(self.is_running)
            self.check_simulation_done()
            self.draw_text_and_graph_borders()
            self.stats_table.update()
            self.draw_error()
            py.display.flip()
            self.clock.tick(self.fps)
        py.quit()

    def event_check(self) -> None:
        """checks every event to determine if an action is needed"""
        global button_changed
        for event in py.event.get():
            # exit window
            if event.type == py.QUIT:
                self.done = True
            if event.type == py.MOUSEWHEEL:
                self.check_mouse_wheel(event)
            if event.type == py.MOUSEBUTTONDOWN:
                self.check_mouse_button_down(event)
            if event.type == py.KEYDOWN and self.active_button is not None:
                self.check_button_press(event)

    def check_mouse_wheel(self, event: pygame.event.Event) -> None:
        """Checks for the mouse wheel event

        Preconditions:
        - event is not None
        """
        dy = event.y
        x, y = py.mouse.get_pos()
        if self.stats_table is not None:
            self.stats_table.check_scroll(x, y, dy)

    def check_mouse_button_down(self, event: pygame.event.Event) -> None:
        """Checks for the mouse button down event

        Preconditions:
        - event is not None
        """
        global button_changed
        if self.active_button is not None:
            self.active_button.active = False
            self.active_button = None
        for b in self.buttons.values():
            if b.rect.collidepoint(event.pos) and (not self.is_running or not isinstance(b, InputButton)):
                b.active = True
                self.active_button = b
                break
        # if statements to check for buttons
        if self.active_button is self.buttons['brownian']:
            self.active_button.background_color = GREEN if self.active_button.background_color == RED else RED
            self.simulation.brownian = self.active_button.background_color == GREEN
        if self.active_button is self.buttons['run'] and not self.is_running:
            self.is_running = True
            if self.simulation.simu_graph.infected == set():
                button_changed = True
        if self.active_button is self.buttons['regen']:
            self.is_running = False
            button_changed = True
            if not all(button.text != '' for button in self.buttons.values() if
                       isinstance(button, InputButton) and button is not self.buttons['brownian']):
                self.draw_run_error = True
                self.can_initialize_run = True
                self.is_running = False

    def check_button_press(self, event: pygame.event.Event) -> None:
        """checks for button press only if self.active button is not none

        Preconditions:
        - event is not None
        """
        global button_changed
        if event.key == py.K_BACKSPACE:
            # may need more functionality later
            if isinstance(self.active_button, InputButton):
                self.active_button.text = self.active_button.text[:-1]
                button_changed = True
        # takes care of integer input boxes
        elif isinstance(
                self.active_button,
                InputButton) and self.active_button.input_type == 'int':
            try:
                int(event.unicode)
            except ValueError:
                pass
            else:
                self.active_button.update_text(event.unicode)
        # takes care of floating point input boxes
        elif isinstance(self.active_button, InputButton):
            # stores the current button's text plus what the user just inputted
            possible_text = self.active_button.text + event.unicode
            try:
                float(possible_text)
            except ValueError:
                pass
            else:
                self.active_button.update_text(event.unicode)

    def update_buttons(self) -> None:
        """loops over every button and calls its update function"""
        for b in self.buttons:
            # updates bounds for initial infected
            if b == 'initial':
                self.buttons[b].change_bound((1,
                                              int(self.buttons['fam_pop'].text) * int(self.buttons['fam'].text) + 1 if
                                              self.buttons['fam_pop'].text != '' and self.buttons[
                                                  'fam'].text != '' else 1))
                if self.buttons[b].text != '':
                    self.buttons[b].text = str(min(
                        int(self.buttons[b].text),
                        int(self.buttons['fam_pop'].text) * int(self.buttons['fam'].text) if
                        self.buttons['fam_pop'].text != '' and self.buttons['fam'].text != '' else 1))
            self.buttons[b].update()

    def update_data_objects(self) -> None:
        """updates the GUI objects depending on if an input was changed on the front end"""
        global button_changed
        if button_changed:
            if all(button.text != '' for button in self.buttons.values() if
                   isinstance(button, InputButton) and button is not self.buttons['brownian']):
                num_families = int(self.buttons['fam'].text)
                family_size = int(self.buttons['fam_pop'].text)
                population = num_families * family_size
                speed = int(self.buttons['speed'].text)
                recovery = float(self.buttons['recover'].text)
                infectivity = float(self.buttons['infect'].text)
                inital_infected = int(self.buttons['initial'].text)
                close_contact_distance = int(self.buttons['close'].text)
                self.simulation = sim(num_families, family_size, speed + 1, int(self.fps * recovery), inital_infected,
                                      close_contact_distance, self.fps, infectivity,
                                      self.buttons['brownian'].background_color == GREEN)
                self.main_graph = self.simulation.simu_graph
                self.stacked_graph = StackedAreaGraph(population, self.main_graph)
                self.stats_table = StatsTable(num_families, self.simulation)
                self.done_frames = 0
            button_changed = False

    def check_error_fields(self) -> None:
        """checks if all input fields are valid before running the simulation"""
        if self.is_running and self.can_initialize_run:
            self.can_initialize_run = False
            if not all(button.text != '' for button in self.buttons.values() if
                       isinstance(button, InputButton) and button is not self.buttons['brownian']):
                self.draw_run_error = True
                self.can_initialize_run = True
                self.is_running = False

    def draw_main_graph(self) -> None:
        """draws the main graph on the display"""
        # Updates the main graph edges
        for k in self.main_graph.id_to_person.values():
            for n in self.main_graph.id_to_person.values():
                if k.family_id == n.family_id:
                    x = n.location[0]
                    y = n.location[1]
                    draw_edge((k.location[0] + 25, k.location[1] + 25), (x + 25, y + 25), WHITE)
        for j in self.main_graph.infected:
            for m in j.close_contact:
                x = self.main_graph.id_to_person[m].location[0]
                y = self.main_graph.id_to_person[m].location[1]
                draw_edge((j.location[0] + 25, j.location[1] + 25), (x + 25, y + 25), RED)
        # Update the main graph nodes
        for j in self.main_graph.infected:
            x = j.location[0]
            y = j.location[1]
            draw_node((x + 25, y + 25), (255, 0, 0))
        for k in self.main_graph.recovered:
            x = k.location[0]
            y = k.location[1]
            draw_node((x + 25, y + 25), (0, 0, 255))
        for family_id in range(1, self.simulation.num_family + 1):
            for person in self.simulation.id_to_family[family_id]:
                if person.state != INFECTED:
                    draw_node((person.location[0] + 25, person.location[1] + 25), COLORS[family_id - 1])

    def check_simulation_done(self) -> None:
        """checks if the simulation is done"""
        if self.active_button is self.buttons['stop']:
            self.is_running = False
            self.can_initialize_run = True
        if self.simulation.simu_graph.infected == set():
            if self.done_frames == self.fps:
                draw_text(25, 5, 'SIMULATION FINISHED', 15, GREEN)
                self.is_running = False
                self.can_initialize_run = True
                self.done_frames = self.fps
            else:
                self.done_frames += 1

    def draw_text_and_graph_borders(self) -> None:
        """draws the button label texts and the graph outlines"""
        main_block = py.Rect(25, 25, 500, 500)
        py.draw.rect(screen, SKY_BLUE, main_block, 1)
        second_block = py.Rect(600, 300, STACKED_GRAPH_LENGTH,
                               STACKED_GRAPH_HEIGHT)
        py.draw.rect(screen, SKY_BLUE, second_block, 1)
        # Drawing the text along with its bounds
        draw_text(120, 580, 'FAMILY SIZE', 15, WHITE)
        draw_text(150, 600, '(max 50)', 15, WHITE)

        draw_text(140, 530, 'FAMILIES', 15, WHITE)
        draw_text(150, 550, '(max 20)', 15, WHITE)

        draw_text(345, 580, 'INFECTIVITY', 15, WHITE)
        draw_text(345, 600, '(max 1.0)', 15, WHITE)

        draw_text(310, 530, 'INITIAL INFECTED', 15, WHITE)
        draw_text(350, 550, f'(max {self.simulation.num_family * self.simulation.family_size})', 15, WHITE)

        draw_text(540, 530, 'CONTACT DISTANCE', 15, WHITE)
        draw_text(625, 550, '(max 999)', 15, WHITE)

        draw_text(640, 580, 'SPEED', 15, WHITE)
        draw_text(635, 600, '(max 20)', 15, WHITE)

        draw_text(790, 530, 'RECOVERY PERIOD', 15, WHITE)
        draw_text(860, 550, '(max 9999)', 15, WHITE)

        draw_text(850, 580, 'BROWNIAN', 15, WHITE)

    def draw_error(self) -> None:
        """draws error if draw_run_error is true"""
        if self.draw_run_error:
            if self.error_timer == 0:
                self.error_timer = self.fps
                self.draw_run_error = False
            self.error_timer -= 1
            draw_text(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, 'ALL INPUTS MUST BE VALID', 50, RED)


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
              font_color: tuple[int, int, int]) -> None:
    """ Draws text on the screen

    Preconditions:
    - SCREEN_HEIGHT >= x >= 0 and SCREEN_WIDTH >= y >= 0
    - text != ''
    - font_size > 0
    - len(font_color) == 3 and all(255 >= x >= 0 for x in font_color)
    """
    comic_sans = py.font.SysFont('arial', font_size)
    text_render = comic_sans.render(text, True, font_color)
    screen.blit(text_render, (x, y))


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': ['runner'],  # the names (strs) of functions that call print/open/input
        'disable': ['E9992', 'E9997', 'E1101', 'E9999', 'C0103', 'R0902', 'R0912', 'R0913', 'R0914', 'R1702', 'R0915'],
        'max-line-length': 120
    })
