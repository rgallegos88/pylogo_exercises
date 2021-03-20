# Import the string constants you need (mainly keys) as well as classes and gui elements
from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, LINK_PROB, TBD, graph_left_upper,
                                  graph_right_upper)
from core.sim_engine import gui_set, gui_get
from core.pairs import center_pixel
from core.link import Link
from core.gui import STAR
from random import randint

class Graph_Algorithms_World(Graph_World):

    # noinspection PyMethodMayBeStatic
    def average_path_length(self):
        return TBD

    # noinspection PyMethodMayBeStatic
    def clustering_coefficient(self):
        return TBD

    def compute_metrics(self):
        cluster_coefficient = self.clustering_coefficient()
        gui_set(CLUSTER_COEFF, value=cluster_coefficient)
        avg_path_length = self.average_path_length()
        gui_set(PATH_LENGTH, value=avg_path_length)

    @staticmethod
    def link_nodes_for_graph(graph_type, nbr_nodes, ring_node_list):
        """
        Link the nodes to create the requested graph.

        Args:
            graph_type: The name of the graph type.
            nbr_nodes: The total number of nodes the user requested.
                       (Will be > 0 or this method won't be called.)
            ring_node_list: The nodes that have been arranged in a ring.
                            Will contain either:
                            nbr_nodes - 1 if graph type is STAR or WHEEL
                            or nbr_nodes otherwise

        Returns: None

        Overrides this function from graph_framework.
        """
        print("\n\nlink_nodes_for_graph: Your code goes here.")

        # ! central node is needed if graph type is wheel or star
        center_node = None
        if graph_type in ['wheel', 'star']:
            center_node = Graph_Node()
            center_node.move_to_xy(center_pixel())

            # ! The ring_list is empty
        if not ring_node_list:
            return

        # ! if the graph type is wheel or star and there is only one node, link the lone node to itself 
        if len(ring_node_list) == 1:
            if graph_type in ['wheel', 'star']:
                Link(center_node, ring_node_list[0])
            return
        # ! there is more than one node
        for (node_a, node_b) in zip(ring_node_list, ring_node_list[1:] + [ring_node_list[0]]):

            # ! if user sets 4 nodes
            # ! [1, 2, 3, 4] --> (1,2), (2,3), (3, 1) --> node 4 is the center node
    

            if graph_type in ['wheel', 'ring']:
                Link(node_a, node_b)
            
            # ! the center node gets linked to each other node
            # ! node 4 is linked to nodes 1, 2, 3 based on the example above
            if graph_type in ['wheel', 'star']:
                Link(center_node, node_a)

        
        # ! complete the ring
        # if graph_type in ['wheel', 'ring']:
        #     Link(ring_node_list[-1], ring_node_list[0])

        if graph_type in ['random']:
            link_probability = gui_get(LINK_PROB)
            links = (Link(ring_node_list[i], ring_node_list[j]) 
                                                for i in range(nbr_nodes - 1) 
                                                for j in range(i + 1, nbr_nodes) 
                                                if randint(1, 100) <= link_probability)
            for _ in links:
                pass
            return

        # Small World
        if graph_type in['small world']:

            link_probability = gui_get(LINK_PROB)
            for i in range(nbr_nodes):
                if randint(1,100) <= link_probability:
                    #Link to 2 random nodes if we hit the link_probability
                    for i in range(0,3):
                        r = randint(1,nbr_nodes-1)
                        if r != i:
                            Link(ring_node_list[i],ring_node_list[r]) 

                else:
                    #Otherwise link to the next 2 nodes in line
                    Link(ring_node_list[i],ring_node_list[(i+1)% nbr_nodes])
                    Link(ring_node_list[i],ring_node_list[(i+2)% nbr_nodes]) 

            return

if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=False)
