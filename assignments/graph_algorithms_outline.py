# Import the string constants you need (mainly keys) as well as classes and gui elements
from core.graph_framework import (CLUSTER_COEFF, Graph_Node, Graph_World, PATH_LENGTH, TBD, graph_left_upper,
                                  graph_right_upper)
from core.sim_engine import gui_set, gui_get
from core.pairs import center_pixel
from core.link import Link
from core.gui import STAR


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

        # ! central node is needed if graph type is wheel or star
        center_node = None
        if graph_type in ['wheel', 'star']:
            center_node = Graph_Node()
            center_node.move_to_xy(center_pixel())
            print("the center node was created")

            # ! The ring_list is empty
        if not ring_node_list:
            return

        # ! if the graph type is wheel or star and there is only one node, link the lone node to itself 
        if len(ring_node_list) == 1:
            if graph_type in ['wheel', 'star']:
                Link(center_node, ring_node_list[0])
            return
        for (node_a, node_b) in zip(ring_node_list, ring_node_list[1:] + [ring_node_list[0]]):
            
            if graph_type in ['wheel', 'ring']:
                Link(node_a, node_b)
            
            if graph_type in ['wheel', 'star']:
                Link(center_node, node_a)

        
        # ! complete the ring
        if graph_type in ['wheel', 'ring']:
            Link(ring_node_list[-1], ring_node_list[0])

        print("\n\nlink_nodes_for_graph: Your code goes here.")


if __name__ == '__main__':
    from core.agent import PyLogo
    PyLogo(Graph_Algorithms_World, 'Network test', gui_left_upper=graph_left_upper,
           gui_right_upper=graph_right_upper, agent_class=Graph_Node,
           clear=True, bounce=True, auto_setup=False)
