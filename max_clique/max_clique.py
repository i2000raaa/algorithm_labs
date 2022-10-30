import random
from collections import Counter
import sys

def get_neighbours(node, nodes, adj_matrix):
    return [i for i in range(nodes) if adj_matrix[node][i] == 1]

def get_neigh_dict(nodes, adj_matrix):
    dict_nodes = {}
    for node in range(nodes):
        dict_nodes[node] = get_neighbours(node, nodes, adj_matrix)
    sorted_nodes = {k: v for k, v in sorted(dict_nodes.items(), key=lambda item: len(item[1]), reverse=True)}
    return sorted_nodes

def get_connected_vertices(ver, ver_list, adj_matrix):
    connected_ver_list = []
    for vertice in ver_list:
        if (adj_matrix[vertice][ver] == 1):
            connected_ver_list.append(vertice)
    return connected_ver_list

def max_clique_search(nodes, adj_matrix):
    clique_winner = []
    sorted_nodes = get_neigh_dict(nodes, adj_matrix)
    for i in range(nodes*50):
        length_of_random = int(0.2*nodes)
        start_ver = random.choice(list(sorted_nodes.keys())[:length_of_random])
        candidates = get_neighbours(start_ver, nodes, adj_matrix)
        tmp_clique = []
        tmp_clique.append(start_ver)
        while(len(candidates) != 0):
            ver = random.choice(candidates)
            tmp_clique.append(ver)
            candidates = get_connected_vertices(ver, candidates, adj_matrix)
        if len(tmp_clique) > len(clique_winner):
            clique_winner = tmp_clique
            clique_size = len(clique_winner)
    return clique_winner, clique_size

def check(nodes, clique_winner, adj_matrix):
    counter = Counter(clique_winner)

    if sum(counter.values()) > len(counter):
        print("Duplicates in the clique\n")
        sys.exit()
    
    for i in clique_winner:
        neigh = get_neighbours(i, nodes, adj_matrix)
        for j in clique_winner:
            if i != j and j not in neigh:
                print("Unconnected vertices in the clique\n")
                sys.exit()
    return True
