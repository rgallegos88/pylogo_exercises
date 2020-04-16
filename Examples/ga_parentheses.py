
from __future__ import annotations

from collections import namedtuple
from itertools import count
from math import ceil
from random import choice, randint, sample
from typing import List, Sequence, Tuple

from pygame.color import Color

import core.gui as gui
from core.ga import Chromosome, GA_World, Individual, gui_left_upper
from core.sim_engine import SimEngine
from core.world_patch_block import World

Gene = namedtuple('Gene', ['id', 'val'])


class Parentheses_Chromosome(Chromosome):

    def compute_chromosome_fitness(self) -> Tuple[List[bool], int]:
        len_chrom = len(self)
        # A chromosome is a tuple of Genes, each of which is a Gene(id, val), where val 0 or 1.
        errors = 0
        balance = 0
        balance_value = {'(': 1, ' ': 0, ')': -1}
        satisfied = [True]*len_chrom
        for i in range(len_chrom):
            balance += balance_value[self[i].val]
            if balance < 0:
                errors += 1
                balance = 0
                satisfied[i] = False
        fitness = errors
        return (satisfied, fitness)

    def chromosome_string(self):
        return ' '.join([str(gene.val) for gene in self])

    def exchange_genes(self, satisfied) -> Sequence[int]:
        len_chrom = len(self)
        candidate_zero_indices = self.unsatisfied_value_indices(0, satisfied, len_chrom)
        if not candidate_zero_indices:
            return self
        candidate_one_indices = self.unsatisfied_value_indices(1, satisfied, len_chrom)
        if not candidate_one_indices:
            return self

        (zero_index, one_index) = (choice(candidate_zero_indices), choice(candidate_one_indices))

        c_list: List[int] = list(self)
        (c_list[zero_index], c_list[one_index]) = (c_list[one_index], c_list[zero_index])

        return c_list

    def gene_value_indices(self, value, length):
        indices = [i for i in range(length) if self[i].val == value]
        return indices

    def is_satisfied(self, i, len_chrom) -> bool:
        """
        Is chrom[i] satisfied?
        It is satisfied if at least 2 of the four elements on either side (2 on each side) have the same value.
        """
        if self[i].val == ' ':
            return True
        neigh_indices = [p for p in range(i-2, i+3) if p != i]
        # Use mod (%) so that we can wrap around. (Negatve wrap-around is automatic!)
        matches = [1 if self[p % len_chrom].val == self[i].val else
                   0 if self[p % len_chrom].val == ' ' else
                   -1
                   for p in neigh_indices]
        sum_matches = sum(matches)
        satisfied = sum_matches < 0 if SimEngine.gui_get('div_or_seg') == 'Diversity' else \
                    sum_matches > 0 if SimEngine.gui_get('div_or_seg') == 'Segregation' else \
                    sum_matches == 0
        return satisfied

    def move_unsatisfied_gene(self, candidate_indices) -> Sequence[Gene]:
        """
        This mutation operator moves a gene from one place to another.
        This version selects an unsatisfied gene to move.
        """
        from_index = choice(candidate_indices)
        gene_to_move: Gene = self[from_index]
        list_chromosome: List[Gene] = list(self)
        revised_list: List[Gene] = list_chromosome[:from_index] + list_chromosome[from_index+1:]
        indices = list(range(len(revised_list)))
        if from_index in indices:
            indices.remove(from_index)
        to_index = choice(indices)
        revised_list.insert(to_index, gene_to_move)
        return revised_list

    def unsatisfied_value_indices(self, value, satisfied, length):
        unsatisfied_indices = [i for i in range(length) if self[i].val == value and not satisfied[i]]
        space_indices = [i for i in range(length) if self[i].val == ' ']
        return unsatisfied_indices + space_indices


class Parentheses_Individual(Individual):

    def __init__(self, chromosome: Sequence[Gene]):
        self.satisfied = None
        self.chromosome: Parentheses_Chromosome = Parentheses_Chromosome(chromosome)
        super().__init__(self.chromosome)

    def __str__(self):
        return f'{self.fitness}: ' \
               f'{self.chromosome.chromosome_string()}' \
               f'\n' \
               f'{" "*len(str(self.fitness))}  {Parentheses_Individual.satisfied_string(self.satisfied)}'

    def compute_fitness(self) -> float:
        (self.satisfied, fitness) = self.chromosome.compute_chromosome_fitness()
        return fitness

    def mate_with(self, other):
        return self.cx_uniform(other)

    def mutate(self) -> Individual:
        chromosome = self.chromosome
        satisfied = self.satisfied

        no_mutation = SimEngine.gui_get('no_mutation')
        move_unsatisfied = SimEngine.gui_get('move_unsatisfied_gene')
        exchange_genes = SimEngine.gui_get('exchange_genes')
        move_gene = SimEngine.gui_get('move_gene')
        reverse_subseq = SimEngine.gui_get('reverse_subseq')

        mutations_options = move_unsatisfied + exchange_genes + move_gene + reverse_subseq + no_mutation
        mutation_choice = randint(0, mutations_options)

        if mutation_choice <= move_unsatisfied:
            unsatisfied_indices = [i for i in range(len(satisfied)) if not satisfied[i]]
            if not unsatisfied_indices:
                return self
            new_chromosome = chromosome.move_unsatisfied_gene(unsatisfied_indices)

        elif mutation_choice <= move_unsatisfied + exchange_genes:
            assert isinstance(self.chromosome, Parentheses_Chromosome)
            new_chromosome = chromosome.exchange_genes(satisfied)

        elif mutation_choice <= move_unsatisfied + exchange_genes + move_gene:
            new_chromosome = chromosome.move_gene()

        elif mutation_choice <= move_unsatisfied + exchange_genes + move_gene + reverse_subseq:
            new_chromosome = chromosome.reverse_subseq()

        else:
            return self

        new_individual = GA_World.individual_class(new_chromosome)
        return new_individual

    @staticmethod
    def satisfied_string(satisfied: List[bool]):
        sat_str = f'{" ".join([" " if satisfied[i] else "^" for i in range(len(satisfied))])}'
        return sat_str


class Parentheses_World(GA_World):

    world = None

    def __init__(self, *arga, **kwargs):
        super().__init__(*arga, **kwargs)
        # self.chromosome_length = None

    @staticmethod
    def display_best_ind(best_ind: Parentheses_Individual):
        # Parentheses_World.insert_chrom_and_sats(best_ind, best_ind.chromosome, best_ind.satisfied)
        print(str(best_ind))

    def gen_gene_pool(self):
        chromosome_length = SimEngine.gui_get('chrom_length')
        lefts_rights = chromosome_length//2
        lefts = ['('] * lefts_rights
        rights = [')'] * lefts_rights
        GA_World.gene_pool = sample(lefts + rights, chromosome_length)

    def gen_individual(self):
        chromosome_tuple: Tuple[Gene] = GA_World.chromosome_class(Gene(id, val)
                                                                  for (id, val) in zip(count(), GA_World.gene_pool))
        individual = GA_World.individual_class(chromosome_tuple)
        return individual

    @staticmethod
    def insert_chrom_and_sats(best_ind, chromosome, satisfied, window_rows=2):
        """ Scroll the screen and insert the current best chromosome with unsatisfied genes indicated. """
        Parentheses_World.scroll_window(window_rows)

        # chrom_string = chromosome.chromosome_string()
        # green = Color('springgreen3')
        # yellow = Color('yellow')
        # blue = Color('lightblue')
        # val_to_color = {'(': yellow, ')': green}
        indentation = ceil((gui.PATCH_COLS - len(chromosome))/2)
        # print(indentation, len(chromosome), gui.PATCH_COLS)
        chrom_str = f'{chromosome.chromosome_string()}'
        sats_str = f'{Parentheses_Individual.satisfied_string(satisfied)}'

        # best_str = str(best_ind)
        World.patches_array[gui.PATCH_ROWS - 2, indentation].label = chrom_str
        World.patches_array[gui.PATCH_ROWS - 1, indentation].label = sats_str
        # for c in range(len(chromosome)):
        #     # patch_color = val_to_color[chromosome[c].val]
        #     World.patches_array[gui.PATCH_ROWS-2, indentation+c].label = chromosome[c].val
        # red = Color('red')
        # black = Color('black')
        # for c in range(len(satisfied)):
        #     World.patches_array[gui.PATCH_ROWS-1, indentation+c].set_color(black if satisfied[c] else red)

    @staticmethod
    def scroll_window(window_rows):
        """ Scroll the screen up by window-rows lines """
        for i in range(0, gui.PATCH_ROWS, window_rows):
            for r in range(window_rows):
                if i + r + window_rows < gui.PATCH_ROWS:
                    for c in range(gui.PATCH_COLS):
                        World.patches_array[i + r, c].set_color(World.patches_array[i + r + window_rows, c].color)

    def set_results(self):
        """ Find and display the best individual. """
        super().set_results()
        # noinspection PyTypeChecker
        Parentheses_World.display_best_ind(self.best_ind)

    def setup(self):
        GA_World.individual_class = Parentheses_Individual
        GA_World.chromosome_class = Parentheses_Chromosome
        Parentheses_World.world = self
        # Block.patch_text_offset = 10
        # chromosome_length = SimEngine.gui_get('chrom_length')
        # print('_'*(2*SimEngine.gui_get('chrom_length')+5))
        super().setup()


# ########################################## Parameters for demos ######################################## #
# patch_size = 5
# patch_size = 8
patch_size = 11

board_size = (70//patch_size)*10
# ############################################## Define GUI ############################################## #
import PySimpleGUI as sg
seg_gui_left_upper = gui_left_upper \
                     + [
                        [sg.Text('Prob no mutation', pad=((0, 5), (10, 0))),
                         sg.Slider(key='no_mutation', range=(0, 100), resolution=1, default_value=10,
                                   orientation='horizontal', size=(10, 20))
                         ],

                         [sg.Text('Prob move unsatisfied gene', pad=((0, 5), (20, 0))),
                          sg.Slider(key='move_unsatisfied_gene', range=(0, 100), default_value=5,
                                    orientation='horizontal', size=(10, 20))
                          ],

                        [sg.Text('Prob exchange two genes', pad=((0, 5), (20, 0))),
                         sg.Slider(key='exchange_genes', range=(0, 100), default_value=5,
                                   orientation='horizontal', size=(10, 20))
                         ],

                        [sg.Text('Prob move gene', pad=((0, 5), (20, 0))),
                         sg.Slider(key='move_gene', range=(0, 100), default_value=5,
                                   orientation='horizontal', size=(10, 20))
                         ],

                        [sg.Text('Prob reverse subseq', pad=((0, 5), (20, 0))),
                         sg.Slider(key='reverse_subseq', range=(0, 100), default_value=5,
                                   orientation='horizontal', size=(10, 20))
                         ],

                        [sg.Text('Fitness target', pad=((0, 5), (20, 0))),
                         sg.Slider(key='fitness_target', default_value=0, enable_events=True,
                                   orientation='horizontal', size=(10, 20), range=(0, 10))
                         ],

                        [sg.Text('Chromosome length', pad=(None, (20, 0))),
                         sg.Slider(key='chrom_length', range=(2, board_size), enable_events=True, size=(10, 20),
                                   pad=((10, 0), (0, 0)), orientation='horizontal', default_value=board_size,
                                   resolution=2)
                         ],

                        ]


if __name__ == "__main__":
    from core.agent import PyLogo
    PyLogo(Parentheses_World, 'GA Segregation', seg_gui_left_upper,
           patch_size=patch_size, board_rows_cols=(board_size, board_size))