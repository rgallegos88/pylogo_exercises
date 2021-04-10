from random import randint

from pygame.color import Color

from core.agent import Agent
from core.gui import PATCH_COLS, PATCH_ROWS
from core.sim_engine import SimEngine
from core.world_patch_block import Patch, World

#route definitions
TOP_ROUTE = 0
BOTTOM_ROUTE = 1
BRAESS_ROAD_ROUTE = 2

#road definitions
VARIABLE_CONGESTION = 0 # top and bottom horizontal roads
CONSTANT_CONGESTION = 1 # left and right vertical roads
BRAESS_ROAD_ENABLED = 2
BRAESS_ROAD_DISABLED = 3

CONSTANT_CONGESTION_DELAY = 15


class Road_Patch(Patch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.road_type = None
        self.delay = 1

class Commuter(Agent):
    def __init__(self, birth_tick=None, route=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks_here = 1
        self.birth_tick= birth_tick
        self.route = route
        self.commute_complete = False

        if route == TOP_ROUTE or route == BRAESS_ROAD_ROUTE:
            self.face_xy(Braess_Road_World.top_right.center_pixel)
        else:
            print("what is going on")
            self.face_xy(Braess_Road_World.bottom_left.center_pixel)

    def move(self):
        if self.commute_complete == False:
            if self.ticks_here < self.current_patch().delay:
                self.ticks_here += 1
            else:
                SOUTH = 180
                EAST = 90
                SOUTH_WEST = None
                if self.heading == EAST:
                    self.move_to_patch(World.patches_array[self.current_patch().row][self.current_patch().col + 1])
                elif self.heading == SOUTH:
                    self.move_to_patch(World.patches_array[self.current_patch().row + 1][self.current_patch().col])
                #braess road segment move
                else:
                    self.move_to_patch(World.patches_array[self.current_patch().row + 1][self.current_patch().col - 1])


                if self.current_patch() == Braess_Road_World.top_right and self.route == TOP_ROUTE:
                    self.face_xy(Braess_Road_World.bottom_right.center_pixel)
                if self.current_patch() == Braess_Road_World.top_right and self.route == BRAESS_ROAD_ROUTE:
                    self.face_xy(Braess_Road_World.bottom_left.center_pixel)
                if self.current_patch() == Braess_Road_World.bottom_left:
                    self.face_xy(Braess_Road_World.bottom_right.center_pixel)
                if self.current_patch() == Braess_Road_World.bottom_right:

                    #there is an extra number of ticks equal to delay so we remove them here
                    if self.route == BRAESS_ROAD_ROUTE:
                        self.birth_tick = self.birth_tick + 5
                    self.commute_complete = True
                self.ticks_here = 1

        # increase the birth ticks by one for each tick that the commuter is on braess road
        # this removes the extra time that the commuter is on the road
        if self.current_patch().road_type == BRAESS_ROAD_ENABLED or ():
            # print('braess road branch')
            self.birth_tick += 1

    

class Braess_Road_World(World):


    travel_time = None #travel time of last turtle to complete route
    top = None #travel time of last turtle to complete top route
    bottom = None #travel time of last turtle to complete bottom route
    middle = None # travel time of last turtle to complete middle route
    spawn_time = None # next tick to spawn a new turtle
    spawn_rate = None
    middle_prev = False # previous status of middle route
    avg = None # total average of travel time (smoothed)
    cars_spawned = None # total number of active commuters
    top_prob = None # probability for agent to take top route
    bottom_prob = None # probability for agent to take bottom route
    middle_prob = None # probability for agent to take middle route
    middle_active = False
    ticks = None
    top_left = None # patch that is the top-left node of the grid
    top_right = None # patch that is the top-right node of the grid
    bottom_right = None # patch that is the bottom-right node of the grid
    bottom_left = None # patch that is the bottom-left node of the grid

    def __init__(self, *args, **kwargs):
        # self.patch_class = Road_Patch
        # self.spawn_list = []
        super().__init__(*args, **kwargs)

        Braess_Road_World.top_left= World.patches_array[2][2]
        Braess_Road_World.top_right = World.patches_array[2][PATCH_COLS - 3]
        Braess_Road_World.bottom_left = World.patches_array[PATCH_ROWS - 3][2]
        Braess_Road_World.bottom_right = World.patches_array[PATCH_ROWS - 3][PATCH_COLS - 3]
        
        
        self.setup()
    

    def commuter_stats(self, commuter):
        # calculates travel times and adds them to the appropurate route tracker

        # rate is the frame rate at wchich the sim is running
        travel_time = (World.ticks - commuter.birth_tick)
        # print(travel_time)
        # return
        smoothing = SimEngine.gui_get(SMOOTHING)
        # calculate avge traveltime across completed commutes
        if self.avg == 0:
            self.avg = travel_time
            print(self.avg)
        else:
            # based on number of 20 agents
            self.avg = ((19 * self.avg + travel_time) / 20)
            print(self.avg)

        # if the route is a _______
        if commuter.route == TOP_ROUTE:
            # top ; travel time of last turtle to complete top route
            if self.top == 0:
                self.top = travel_time
            else:
                self.top = ((travel_time) + ((smoothing - 1) * self.top)) / smoothing
        else:
            if commuter.route == BOTTOM_ROUTE:
                if self.bottom == 0:
                    self.bottom = travel_time
                else:
                    self.bottom = ((travel_time) + ((smoothing - 1) * self.bottom)) / smoothing
            #triggers on route with braess road
            else:
                if self.middle == 0:
                    self.middle = travel_time
                else:
                    self.middle = ((travel_time) + ((smoothing - 1) * self.middle)) / smoothing
        self.update_gui_data()
    

    def set_roads(self, road_type, start_patch: Patch, stop_patch: Patch):
        if road_type == VARIABLE_CONGESTION:
            start_patch = World.patches_array[start_patch.row][start_patch.col + 1]
            stop_patch = World.patches_array[stop_patch.row][stop_patch.col - 1]

            #draw and set the middle line
            for p in self.draw_line(start_patch, stop_patch):
                p.set_color(Color('Yellow'))
                p.road_type = VARIABLE_CONGESTION

                World.patches_array[p.row+1][p.col].set_color(Color('Black'))
                World.patches_array[p.row-1][p.col].set_color(Color('Black'))

        if road_type == CONSTANT_CONGESTION:
            start_patch = World.patches_array[start_patch.row+1][start_patch.col]
            stop_patch = World.patches_array[stop_patch.row-1][stop_patch.col]

            # draw and set the middle line
            for p in self.draw_line(start_patch, stop_patch):
                p.set_color(Color('Orange'))
                p.road_type = VARIABLE_CONGESTION

                World.patches_array[p.row][p.col+1].set_color(Color('Black'))
                World.patches_array[p.row][p.col-1].set_color(Color('Black'))

        if road_type == BRAESS_ROAD_ENABLED or road_type == BRAESS_ROAD_DISABLED:
            if road_type == BRAESS_ROAD_ENABLED:
                edge_color = Color('Black')
                middle_color = Color('White')
            else:
                edge_color = Color(64,64,64)
                middle_color = Color(64,64,64)

            start_patch = World.patches_array[start_patch.row + 1][start_patch.col - 1]
            stop_patch = World.patches_array[stop_patch.row - 1][stop_patch.col + 1]

            for p in self.draw_line(start_patch, stop_patch):
                p.road_type = road_type

            for p in self.draw_line(start_patch, stop_patch)[1:-1]:
                p.set_color(middle_color)
                if p in self.draw_line(start_patch, stop_patch)[3:-1]:
                    World.patches_array[p.row + 2][p.col].set_color(edge_color)
                    World.patches_array[p.row][p.col - 2].set_color(edge_color)
                if p in self.draw_line(start_patch, stop_patch)[2:-1]:
                    World.patches_array[p.row][p.col - 1].set_color(edge_color)
                    World.patches_array[p.row+1][p.col].set_color(edge_color)

    
 
    def init_roads(self):
        # color all the patches
        for patch in self.patches:
            color = randint(1,10) + 50
            patch.set_color(Color(0, color, 0))


        # road corners
        self.top_left.set_color(Color('Green'))
        self.top_left.delay = 10
        self.top_right.set_color(Color('Blue'))
        self.top_right.delay = 10
        self.bottom_left.set_color(Color('Blue'))
        self.bottom_left.delay = 10
        self.bottom_right.set_color(Color('Red'))
        self.bottom_right.delay = 10

        # fill in corners
        corner_padding = self.bottom_left.neighbors_8() + self.bottom_right.neighbors_8() + \
                         self.top_left.neighbors_8() + self.top_right.neighbors_8()
        for p in corner_padding:
            p.set_color(Color('Black'))


        self.set_roads(VARIABLE_CONGESTION, self.top_left, self.top_right)
        self.set_roads(VARIABLE_CONGESTION, self.bottom_left, self.bottom_right)
        self.set_roads(CONSTANT_CONGESTION, self.top_left, self.bottom_left)
        self.set_roads(CONSTANT_CONGESTION, self.top_right, self.bottom_right)

        self.check_middle()

        if self.middle_active:
            self.set_roads(BRAESS_ROAD_ENABLED, self.top_right, self.bottom_left)
        else:
            self.set_roads(BRAESS_ROAD_DISABLED, self.top_right, self.bottom_left)
    
        # set the delay in Constant congestion road
        for patch in self.draw_line(self.top_right, self.bottom_right)[1:-1]:
            patch.delay = CONSTANT_CONGESTION_DELAY
        for patch in self.draw_line(self.top_left, self.bottom_left)[1:-1]:
            patch.delay = CONSTANT_CONGESTION_DELAY

        #set the delay in braess road to 1 tick
        for patch in self.draw_line(self.top_right, self.bottom_left):
            patch.set_delay = 1

        # #roads
        # for patch in self.draw_line(self.top_left, self.top_right):
        #     patch.set_color('Yellow')

        
        # for patch in self.draw_line(self.bottom_left, self.bottom_right):
        #     patch.set_color('Yellow')

        # for patch in self.draw_line(self.top_left, self.bottom_left):
        #     patch.set_color('Orange')
        
        # for patch in self.draw_line(self.top_right, self.bottom_right):
        #     patch.set_color('Orange')

        # self.check_middle()

        # if self.middle_active:
        #     for patch in self.draw_line(self.top_right, self.bottom_left):
        #         patch.set_color('White')
        # else:
        #     for patch in self.draw_line(self.top_right, self.bottom_left):
        #         patch.set_color('Dark Grey')

        
 


    def draw_line(self, patch_a: Patch, patch_b: Patch) -> [Patch]:
        patch_line = []

        
        if patch_a.row == patch_b.row:
            start = patch_a if patch_a.col < patch_b.col else patch_b
            end = patch_b if patch_b.col > patch_a.col else patch_a

            for i  in range (0, end.col - start.col + 1):
                patch_line.append(World.patches_array[start.row][start.col + i])
            return patch_line

        if patch_a.col == patch_b.col:
            start = patch_a if patch_a.row < patch_b.row else patch_b
            end = patch_b if patch_b.row > patch_a.row else patch_a

            for i in range(0, end.row - start.row + 1):
                patch_line.append(World.patches_array[start.row + i][end.col])
            return patch_line
        


        start = patch_a if patch_a.col < patch_b.col else patch_b
        stop = patch_b.col if patch_b.col > patch_a.col else patch_a

        if stop.row - start.row < 0:
            for i in range(0, stop.col - start.col + 1):
                patch_line.append(World.patches_array[start.row - i][start.col + i])
            return patch_line


    def check_middle(self):
        if self.middle_active != self.middle_prev:
            if self.middle_active:
                self.draw_line(self.top_right, self.bottom_left)
                self.middle_prev = self.middle_active
            else:
                braess_road_commuters = [x for x in self.agents if x.route == BRAESS_ROAD_ROUTE]
                if len(braess_road_commuters) == 0:
                    self.draw_line(BRAESS_ROAD_DISABLED, self.top_right_patch, self.bottom_left_patch)
                    self.middle_prev = self.middle_active

    def spawn_commuters(self):

        # center_pixel = self.top_left.center_pixel
        # new_Commuter = Commuter(World.ticks, center_pixel=center_pixel, route=0, scale=1.5)
        # new_Commuter.move_to_patch(self.top_left)

        if self.spawn_time >= self.spawn_rate:
            center_pixel = self.top_left.center_pixel
            new_Commuter = Commuter(birth_tick=World.ticks, center_pixel=center_pixel, route=self.select_route(), scale=1.5)
            new_Commuter.move_to_patch(self.top_left)

            self.cars_spawned += 1
            self.spawn_time = 0
        
        else:
            print("adding to the spawn_time")
            self.spawn_time += 1

        
        
        # self.agent_class(birth_tick=World.ticks, center_pixel=center_pixel, route=0, scale=1.4)

        

    def determine_congestion(self):
        trafic_variable_top_road = self.draw_line(self.top_left, self.top_right)[1:-1]
        trafic_variable_top_road_commuters = [x for x in World.agents if x.current_patch() in trafic_variable_top_road]

        delay = len(trafic_variable_top_road_commuters) * SimEngine.gui_get(VARIABLE_CONGESTION_DELAY)

        for patch in trafic_variable_top_road:
            patch.delay = delay
        

        #calcultate the congestion for the bottom road
        delay = 1
        bottom_road = self.draw_line(self.bottom_left, self.bottom_right)[1:-1]
        bottom_road_commuters = [x for x in World.agents if x.current_patch() in bottom_road]

        delay = len(bottom_road_commuters) * SimEngine.gui_get(VARIABLE_CONGESTION_DELAY)
        for patch in bottom_road:
            patch.delay = delay


    def select_route(self):
        if SimEngine.gui_get(SELECTION_ALGORITHM) == EMPIRICAL_ANALYTICAl:
            return self.probabilistic_analytic()
        if SimEngine.gui_get(SELECTION_ALGORITHM) == PROBABILISTIC_GREEDY:
            return self.greedy()
        if SimEngine.gui_get(SELECTION_ALGORITHM) == BEST_KNOWN:
            return self.best_route()
        
    def probabilistic_analytic(self):
        if self.middle_on:
            #find the road times of all segments
            top_road_time = self.road_travel_time(self.top_right, self.bottom_left)
            bottom_road_time = self.road_travel_time(self.bottom_right, self.bottom_left)
            left_road_time = self.road_travel_time(self.top_left, self.bottom_left)
            right_road_time = self.road_travel_time(self.top_right, self.bottom_right)

            #find all the route times
            top_route_time = top_road_time + right_road_time
            middle_route_time = top_road_time + bottom_road_time
            bottom_route_time = left_road_time + bottom_road_time

            #select the one that has the least projected time with the current agents
            if top_route_time < middle_route_time and top_route_time < bottom_route_time:
                return TOP_ROUTE
            if bottom_route_time < middle_route_time and bottom_route_time < top_route_time:
                return BOTTOM_ROUTE
            else:
                return BRAESS_ROAD_ROUTE

        else:
            if randint(0,100) <= int(SimEngine.gui_get(RANDOMNESS)):
                return randint(0,1)
            else:
                top_route_count = len([x for x in World.agents if x.route == TOP_ROUTE])
                bottom_route_count = len([x for x in World.agents if x.route == BOTTOM_ROUTE])
                return TOP_ROUTE if top_route_count < bottom_route_count else BOTTOM_ROUTE


    def greedy(self):
            if self.middle_on:
                if self.latest_middle_time == 0 or self.latest_top_time == 0 or self.latest_bottom_time == 0:
                    return randint(0,2)
                else:
                    top_different = 2 - self.latest_top_time
                    if top_different < 0:
                        top_different = 0
                    top_different = top_different **  (int(SimEngine.gui_get(RANDOMNESS)) / 10)
                    bottom_different = 2 - self.latest_bottom_time
                    if bottom_different < 0:
                        bottom_different = 0
                    bottom_different = bottom_different **  (int(SimEngine.gui_get(RANDOMNESS)) / 10)
                    middle_different = 2 - self.latest_middle_time
                    if middle_different < 0:
                        middle_different = 0
                    middle_different = middle_different ** (int(SimEngine.gui_get(RANDOMNESS)) / 10)

                    sigma1 = 0
                    sigma2 = 0
                    if not (top_different + bottom_different + middle_different) == 0:
                        sigma1 = top_different / (top_different + bottom_different + middle_different)
                        sigma2 = bottom_different / (top_different + bottom_different + middle_different)
                    else:
                        sigma1 = 0.33
                        sigma2 = 0.33

                    self.top_prob = sigma1
                    self.bottom_prob = sigma2
                    self.middle_prob = 1 - sigma1 - sigma2
                    split1 = 1000 * sigma1
                    split2 = 1000 * (sigma1 + sigma2)
                    rand = randint(0, 999)
                    if rand < split1:
                        return 0
                    else:
                        if rand < split2:
                            return 1
                        else:
                            return 2
            else:
                if self.latest_top_time == 0 or self.latest_bottom_time == 0:
                    return randint(0,1)
                else:
                    top_different = (2 - self.latest_top_time) ** (int(SimEngine.gui_get(RANDOMNESS)) / 10)
                    bottom_different = (2 - self.latest_bottom_time) ** (int(SimEngine.gui_get(RANDOMNESS)) / 10)
                    sigma = top_different / (top_different + bottom_different)
                    top_prob = sigma
                    bottom_prop = 1 - sigma
                    split = 1000 * sigma
                    if randint(0, 999) < split:
                        return 0
                    else:
                        return 1

    def probabilistic_analytic(self):
        if self.middle_active:
            #find the road times of all segments
            top_road_time = self.road_travel_time(self.top_right, self.top_left)
            bottom_road_time = self.road_travel_time(self.bottom_right, self.bottom_left)
            left_road_time = self.road_travel_time(self.top_left, self.bottom_left)
            right_road_time = self.road_travel_time(self.top_right, self.bottom_right)

            #find all the route times
            top_route_time = top_road_time + right_road_time
            middle_route_time = top_road_time + bottom_road_time
            bottom_route_time = left_road_time + bottom_road_time

            #select the one that has the least projected time with the current agents
            if top_route_time < middle_route_time and top_route_time < bottom_route_time:
                return TOP_ROUTE
            if bottom_route_time < middle_route_time and bottom_route_time < top_route_time:
                return BOTTOM_ROUTE
            else:
                return BRAESS_ROAD_ROUTE

        else:
            if randint(0,100) <= int(SimEngine.gui_get(RANDOMNESS)):
                return randint(0,1)
            else:
                top_route_count = len([x for x in World.agents if x.route == TOP_ROUTE])
                bottom_route_count = len([x for x in World.agents if x.route == BOTTOM_ROUTE])
                return TOP_ROUTE if top_route_count < bottom_route_count else BOTTOM_ROUTE


    def step(self):
        self.check_middle()
        self.spawn_commuters()
        self.determine_congestion()

        #stores all commuters that have set their end commute flag
        to_remove = []

        for commuter in World.agents:
            commuter.move()
            #check if any commuters have finished their commute
            if commuter.commute_complete:
                self.commuter_stats(commuter)
                to_remove.append(commuter)

        #removes all commuters in the to_remove list
        for commuter in to_remove:
            World.agents.remove(commuter)

    def best_route(self):
        if self.middle_active:
            if self.top == 0 or self.bottom == 0 or self.middle == 0:
                return randint(0, 2)
            else:
                if self.top < self.middle and self.top < self.bottom:
                    return TOP_ROUTE
                if self.middle < self.top and self.middle < self.bottom:
                    return BRAESS_ROAD_ROUTE
                else:
                    return BOTTOM_ROUTE
        else:
            if self.top == 0 or self.bottom == 0:
                return randint(0,1)
            else:
                if self.top < self.bottom:
                    return TOP_ROUTE
                else:
                    return BOTTOM_ROUTE

    def road_travel_time(self, start_patch, stop_patch):
        #find all the commuters on the segment of road
        road = [patch for patch in self.patches_line(start_patch, stop_patch)[1:-1]]

        #calculat e the travel time of the road segment
        road_time = 0
        for patch in road:
            road_time += patch.delay

        return road_time

    def commuters_on_road(self, start_patch, stop_patch):
        road_commuters = []
        road = [patch for patch in self.patches_line(start_patch, stop_patch)[1,:-1]]
        road_commuters.append([commuter for commuter in road if commuter.current_patch() in road])


    def update_gui_data(self):
        SimEngine.gui_set(AVERAGE, value=str(self.avg))
        SimEngine.gui_set(FASTEST_TOP, value=str(self.top))
        SimEngine.gui_set(FASTEST_MIDDLE, value=str(self.middle))
        SimEngine.gui_set(FASTEST_BOTTOM, value=str(self.bottom))

    def update_ticks(self):
        SimEngine.gui_set(TICKS, value=str(self.ticks))



    def setup(self):

        self.travel_time = 0
        self.top = 0
        self.bottom = 0
        self.middle = 0
        self.middle_active = SimEngine.gui_get(MIDDLE_ON)
        self.spawn_time = 0
        self.spawn_rate = SimEngine.gui_get(SPAWN_RATE)
        self.cars_spawned = 0
        self.avg = 0
        self.top = 0
        self.bottom = 0
        self.middle = 0
        self.middle_prev = False
        self.ticks = 0



        self.init_roads()
        self.update_gui_data()

    

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