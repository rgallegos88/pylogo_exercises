from random import randint

from pygame.color import Color

from core.agent import Agent
from core.gui import PATCH_COLS, PATCH_ROWS
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World


class Road_Patch(Patch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.road_type = None
        self.delay = 1

class Commuter(Agent):
    def __init__(self, birth_tick=None, route=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks_here = 1
        self.birth_tick=birth_tick
        self.route = route
        self.commute_complete = False

        # if route == 0 or route == 2 :
        #     self.face_xy(Braess_Road_World.top_right)
        # else:
        #     self.face_xy(Braess_Road_World.bottom_left)

        
            


class Braess_Road_World(World):


    travel_time = None #travel time of last turtle to complete route
    top = None #travel time of last turtle to complete top route
    bottom = None #travel time of last turtle to complete bottom route
    middle = None # travel time of last turtle to complete middle route
    spawn_time = None # next tick to spawn a new turtle
    spawn_rate = None
    middle_prev = None # previous status of middle route
    avg = None # total average of travel time (smoothed)
    cars_spawned = None # total number of active commuters
    top_prob = None # probability for agent to take top route
    bottom_prob = None # probability for agent to take bottom route
    middle_prob = None # probability for agent to take middle route
    top_left = None # patch that is the top-left node of the grid
    top_right = None # patch that is the top-right node of the grid
    bottom_right = None # patch that is the bottom-right node of the grid
    bottom_left = None # patch that is the bottom-left node of the grid

    def __init__(self, *args, **kwargs):
        # self.patch_class = Road_Patch
        # self.spawn_list = []
        super().__init__(*args, **kwargs)
        self.setup()

    
 
    def set_roads(self):
        # color all the patches
        for patch in self.patches:
            color = randint(1,10) + 50
            patch.set_color(Color(0, color, 0))

        

        #roads
        for patch in self.draw_line(self.top_left, self.top_right):
            patch.set_color('Yellow')

        
        for patch in self.draw_line(self.bottom_left, self.bottom_right):
            patch.set_color('Yellow')

        for patch in self.draw_line(self.top_left, self.bottom_left):
            patch.set_color('Orange')
        
        for patch in self.draw_line(self.top_right, self.bottom_right):
            patch.set_color('Orange')

        if SimEngine.gui_get(MIDDLE_ON) == True:
            for patch in self.draw_line(self.top_right, self.bottom_left):
                patch.set_color('White')
        else:
            for patch in self.draw_line(self.top_right, self.bottom_left):
                patch.set_color('Dark Grey')

        
        # road corners
        self.top_left.set_color(Color('Green'))
        self.top_right.set_color(Color('Blue'))
        self.bottom_left.set_color(Color('Blue'))
        self.bottom_right.set_color(Color('Red'))




    def draw_line(self, a: Patch, b: Patch) -> [Patch]:
        patch_line = []
        if b.col == a.col:
            start = a if a.row < b.row else b
            stop = a if a.row > b.row else b
            for i in range(0, stop.row - start.row + 1):
                patch_line.append(World.patches_array[start.row + i][start.col])
            return patch_line

        elif b.row == a.row:
            start = a if a.col < b.col else b
            stop = a if a.col > b.col else b
            for i in range(0, stop.col - start.col + 1):
                patch_line.append(World.patches_array[start.row][start.col + i])
            return patch_line

        start = a if a.col < b.col else b
        stop = a if a.col > b.col else b

        if stop.row - start.row > 0:
            for i in range(0, stop.col - start.col + 1):
                patch_line.append(World.patches_array[start.row + i][start.col + i])
            return patch_line

        if stop.row - start.row < 0:
            for i in range(0, stop.col - start.col +1):
                patch_line.append(World.patches_array[start.row - i][start.col + i])
            return patch_line
    


    def setup(self):
        self.travel_time = 0
        self.top = 0
        self.bottom = 0
        self.middle = 0
        self.spawn_time = 0
        self.spawn_rate = SimEngine.gui_get(SPAWN_RATE)
        self.avg = 0
        self.cars_spawned = 0

        self.top_left = World.patches_array[2][2]
        self.top_left.set_delay = 10

        self.top_right = World.patches_array[2][PATCH_COLS - 3]
        self.top_right.set_delay = 10

        self.bottom_left = World.patches_array[PATCH_ROWS - 3][2]
        self.bottom_left.set_delay = 10
        
        self.bottom_right = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        self.bottom_right.set_delay = 10

        self.num_top = 0
        self.num_bot = 0
        self.num_mid = 0

        self.set_roads()

    

# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
MIDDLE_ON = 'middle_on'
SPAWN_RATE = 'spawn_rate'
SELECTION_ALGORITHM = 'mode'
BEST_KNOWN = 'Best Known'
EMPIRICAL_ANALYTICAl = 'Empirical Analytical'
PROBABILISTIC_GREEDY = 'Probabilistic Greedy'
SMOOTHING = 'Smoothing'
RANDOMNESS = 'Randomness'
AVERAGE = 'average'
FASTEST_TOP = 'fastest top'
FASTEST_MIDDLE = 'fastest middle'
FASTEST_BOTTOM = 'fastest bottom'
VARIABLE_CONGESTION_DELAY = "Dynamic"
TICKS = 'Ticks'

gui_left_upper = [[sg.Text('Middle On?', pad=((0,5), (20,0))), sg.CB('True', key=MIDDLE_ON, pad=((0,5), (10,0)))],
                   [sg.Text('Spawn Rate', pad=((0, 5), (20, 0))),
                    sg.Slider(key=SPAWN_RATE, default_value=60, resolution=10, range=(4, 140), pad=((0, 5), (10, 0)),
                              orientation='horizontal')],
                   [sg.Text('Smoothing', pad=((0, 5), (20, 0))),
                    sg.Slider(key=SMOOTHING, default_value=10, resolution=1, range=(1, 100), pad=((0, 5), (10, 0)),
                              orientation='horizontal')],
                  [sg.Text('mode', pad=((0, 5), (20, 0))),
                   sg.Combo([BEST_KNOWN, EMPIRICAL_ANALYTICAl, PROBABILISTIC_GREEDY], key=SELECTION_ALGORITHM,
                            default_value=BEST_KNOWN, tooltip='Selection Algorithm', pad=((0, 5), (20, 0)))],
                  [sg.Text('Randomness', pad=((0, 5), (20, 0))),
                   sg.Slider(key=RANDOMNESS, default_value=16, resolution=1, range=(0, 100), pad=((0, 5), (10, 0)),
                             orientation='horizontal')],
                  [sg.Text('Dynamic', pad=((0, 5), (20, 0))),
                    sg.Slider(key=VARIABLE_CONGESTION_DELAY, default_value=2, resolution=1, range=(1, 10), pad=((0, 5), (10, 0)),
                              orientation='horizontal')],
                  [sg.Text('Average = '), sg.Text('         0', key=AVERAGE)],
                  [sg.Text('Fastest Top Time = '), sg.Text('         0', key=FASTEST_TOP)],
                  [sg.Text('Fastest Middle Time = '), sg.Text('         0', key=FASTEST_MIDDLE)],
                  [sg.Text('Fastest Bottom Time = '), sg.Text('         0', key=FASTEST_BOTTOM)],
                  [sg.Text('Ticks = '), sg.Text('         0', key=TICKS)]]

from core.agent import PyLogo
# PyLogo(Braess_Road_World, 'Braess Road Paradox', gui_left_upper, bounce=True, patch_size=9, board_rows_cols=(71, 71))
PyLogo(world_class=Braess_Road_World, caption='Braess Road Paradox', agent_class=Commuter,
       gui_left_upper=gui_left_upper, patch_class=Road_Patch)