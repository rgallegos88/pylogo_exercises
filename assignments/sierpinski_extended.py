from __future__ import annotations

from functools import reduce
from random import choice

import core.gui as gui
from core.agent import Agent
from core.sim_engine import gui_get, gui_set, SimEngine
from core.utils import int_round
from core.world_patch_block import World


class Sierpinski_Agent(Agent):

    def __init__(self):
        super().__init__()
        self.label = str(self.id)

class Sierpinski_Extended(World):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self):
        Agent.id = 0
        SimEngine.

    def step(self):
       pass

# ############################################## Define GUI ############################################## #

import PySimpleGUI as sg
# create the board

if __name__ == "__main__":
    from core.agent import PyLogo

    PyLogo(Sierpinski_Extended, 'Sierpinski Extended', agent_class=Sierpinski_Agent)
