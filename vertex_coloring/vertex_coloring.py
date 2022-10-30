global GRAPH_COLORING, COLOR_CNT
import numpy as np
import networkx as nx


def get_neighbours(node, nodes, adj_matrix):
    return [i for i in range(nodes) if adj_matrix[node][i] == 1]

def get_neigh_dict(nodes, adj_matrix):
    dict_nodes = {}
    for node in range(nodes):
        dict_nodes[node] = get_neighbours(node, nodes, adj_matrix)
    sorted_nodes = {k: v for k, v in sorted(dict_nodes.items(), key=lambda item: len(item[1]), reverse=True)}
    return sorted_nodes

def graph_coloring(nodes, adj_matrix):
    global GRAPH_COLORING, COLOR_CNT
    sorted_nodes = get_neigh_dict(nodes, adj_matrix)
    GRAPH_COLORING = {}
    for i in range(nodes):
        GRAPH_COLORING[i] = -1
    G = nx.from_numpy_matrix(adj_matrix)
    if nx.is_connected(G):
        start_node = list(sorted_nodes.keys())[0]
        GRAPH_COLORING[start_node] = 0
        COLOR_CNT = 0
        color_node(start_node, sorted_nodes)
    else:
        commponents_number = nx.number_connected_components(G)
        for i in range(commponents_number):
            if i == 0:
                    start_node = list(sorted_nodes.keys())[0]
                    GRAPH_COLORING[start_node] = 0
                    COLOR_CNT = 0
                    color_node(start_node, sorted_nodes)
            else:
                nxt_comp = [key for key, value in GRAPH_COLORING.items() if value == -1]
                start_node = nxt_comp[0]
                GRAPH_COLORING[start_node] = 0
                color_node(start_node, sorted_nodes) 

def color_node(node, sorted_nodes):
    global GRAPH_COLORING, COLOR_CNT

    neighbours = sorted_nodes[node]
    sorted_neighbours = sorted(neighbours, key=lambda x: len(sorted_nodes[x]), reverse=True)
    for neigh in sorted_neighbours:
        if(GRAPH_COLORING[neigh] == -1):
            current_colors = np.unique(list(filter(lambda x: (x > -1), GRAPH_COLORING.values())))
            neigh_colors = np.unique([GRAPH_COLORING[v] for v in sorted_nodes[neigh] if GRAPH_COLORING[v] > -1])
            available_colors = list(set(current_colors) - set(neigh_colors))
            if(len(available_colors) > 0):
                GRAPH_COLORING[neigh] = available_colors[0]
            else:
                COLOR_CNT += 1
                GRAPH_COLORING[neigh] = COLOR_CNT
            #print(neigh, current_colors, neigh_colors, available_colors)
            color_node(neigh, sorted_nodes)
        else:
            continue


def check(nodes, graph_coloring, adj_matrix):
    for node in range(nodes):
        if(graph_coloring[node] == -1):
            print("ERROR: Uncolored vertice: ", node )
            print(get_neighbours(node, nodes, adj_matrix))
            print(False)
        neighbours = get_neighbours(node, nodes, adj_matrix)
        for neigh in neighbours:
            if graph_coloring[node] == graph_coloring[neigh]:
                print("Neighbour vertices", node, neigh, "have the same color\n")
                print(False)
    return True

def swap_dict(d):
    result = {}
    for k, v in d.items():
            if result.get(v, -2) == -2: 
                result[v] = [k]  
            else:  
                result[v].append(k)
    return result
        