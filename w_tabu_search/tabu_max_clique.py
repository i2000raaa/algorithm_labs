global NEIGHBOUR_SETS, QCO, NON_NEIGHBOURS, BEST_CLIQUE, C_BORDER, Q_BORDER, TIGHT_DICT

from glob import glob
import random
import sys
import random
from collections import Counter


def get_neighbours(node, nodes, adj_matrix):
    return [i for i in range(nodes) if adj_matrix[node][i] == 1]

def get_non_neighbours(node, nodes, adj_matrix):
    return [i for i in range(nodes) if adj_matrix[node][i] == 0]

def get_neigh_dict(nodes, adj_matrix):
    dict_nodes = {}
    for node in range(nodes):
        dict_nodes[node] = get_neighbours(node, nodes, adj_matrix)
    sorted_nodes = {k: v for k, v in sorted(dict_nodes.items(), key=lambda item: len(item[1]), reverse=True)}
    return sorted_nodes

def get_neigh_list(nodes, adj_matrix):
    neigh_list = []
    for node in range(nodes):
        neighbours = get_neighbours(node, nodes, adj_matrix)
        neigh_list.append(neighbours)
    return neigh_list

def get_non_neigh_list(nodes, adj_matrix):
    non_neigh_list = []
    for node in range(nodes):
        non_neighbours = get_non_neighbours(node, nodes, adj_matrix)
        non_neigh_list.append(non_neighbours)
    return non_neigh_list

def get_connected_vertices(ver, ver_list, adj_matrix):
    connected_ver_list = []
    for vertice in ver_list:
        if (adj_matrix[vertice][ver] == 1):
            connected_ver_list.append(vertice)
    return connected_ver_list


def RunSearch(starts, nodes, adj_matrix, randomization):
    global NEIGHBOUR_SETS, QCO, NON_NEIGHBOURS, INDEX, BEST_CLIQUE, C_BORDER, Q_BORDER, TIGHT_DICT
    BEST_CLIQUE = []
    INDEX = [-1 for i in range(nodes)]
    QCO = [0 for i in range(nodes)]
    C_BORDER = 0
    Q_BORDER = 0
    NEIGHBOUR_SETS = get_neigh_list(nodes, adj_matrix)
    NON_NEIGHBOURS = get_non_neigh_list(nodes, adj_matrix)
    TIGHT_DICT = [0 for i in range(nodes)]

    for i in range(starts):
        ClearClique()
        for i in range(len(NEIGHBOUR_SETS)):
            QCO[i] = i
            INDEX[i] = i
            
        RunInitialHeuristic(nodes, adj_matrix, randomization)
        
        C_BORDER = Q_BORDER

        swaps = 0

        while swaps < 100:
            if Move() == False:
                if Swap1To1() == False:
                    break
                else:
                    swaps += 1
                    
        if Q_BORDER > len(BEST_CLIQUE):
            BEST_CLIQUE.clear()

            for i in range(Q_BORDER):
                BEST_CLIQUE.append(QCO[i])
    return BEST_CLIQUE

def ComputeTightness(vertex):
    global QCO, NON_NEIGHBOURS, C_BORDER, Q_BORDER

    tightness = 0
    for i in range(Q_BORDER):
        if vertex in NON_NEIGHBOURS[QCO[i]]:
            tightness += 1
    return tightness

def tightness_dict(nodes):
    global TIGHT_DICT

    TIGHT_DICT = {}
    for node in range(nodes):
        TIGHT_DICT[node] = ComputeTightness(node)
    return TIGHT_DICT


def SwapVertices(vertex, border):
    global QCO

    vertex_at_border = QCO[border]
    QCO[INDEX[vertex]], QCO[border] = QCO[border], QCO[INDEX[vertex]]
    INDEX[vertex], INDEX[vertex_at_border] = INDEX[vertex_at_border], INDEX[vertex]


def InsertToClique(i):
    global NON_NEIGHBOURS, C_BORDER, Q_BORDER, TIGHT_DICT

    for j in NON_NEIGHBOURS[i]:
        if TIGHT_DICT[j] == 0:
            C_BORDER -= 1
            SwapVertices(j, C_BORDER)
        TIGHT_DICT[j] += 1
    
    
    SwapVertices(i, Q_BORDER)
    Q_BORDER += 1
    

def RemoveFromClique(k):
    global QCO, NON_NEIGHBOURS, C_BORDER, Q_BORDER, TIGHT_DICT

    for j in NON_NEIGHBOURS[k]:
        if TIGHT_DICT[j] == 1:
            SwapVertices(j, C_BORDER)
            C_BORDER += 1
        TIGHT_DICT[j] -= 1
    Q_BORDER -= 1
    SwapVertices(k, Q_BORDER)


def Swap1To1():
    global TIGHT_DICT, QCO, NON_NEIGHBOURS, C_BORDER, Q_BORDER
    for counter in range(Q_BORDER):
        vertex = QCO[counter]
        for i in NON_NEIGHBOURS[vertex]:
            if TIGHT_DICT[i] == 1:
                RemoveFromClique(vertex)
                InsertToClique(i)
                return True
    return False

def Move():
    global C_BORDER, Q_BORDER, QCO, BEST_CLIQUE

    if C_BORDER == Q_BORDER:
        return False
    print(len(QCO), Q_BORDER, BEST_CLIQUE)    
    vertex = QCO[Q_BORDER]
    InsertToClique(vertex)
    return True

def RunInitialHeuristic(nodes, adj_matrix, randomization):
    global QCO, NON_NEIGHBOURS, C_BORDER, Q_BORDER, BEST_CLIQUE, NEIGHBOUR_SETS
    b_clique = []
    sorted_nodes = get_neigh_dict(nodes, adj_matrix)
    
    for i in range(nodes*20):
        length_of_random = int(0.2*nodes)
        start_ver = random.choice(list(sorted_nodes.keys())[:length_of_random])
        candidates = get_neighbours(start_ver, nodes, adj_matrix)
        tmp_clique = []
        tmp_clique.append(start_ver)

        while(len(candidates) != 0):
            ver = random.choice(candidates)
            tmp_clique.append(ver)
            candidates = get_connected_vertices(ver, candidates, adj_matrix)
        if len(tmp_clique) > len(b_clique):
            b_clique = tmp_clique
    for vertex in b_clique:
        SwapVertices(vertex, Q_BORDER)
        Q_BORDER += 1
            

def check(nodes, best_clique, adj_matrix):
    counter = Counter(best_clique)

    if sum(counter.values()) > len(counter):
        print("Duplicates in the clique\n")
        sys.exit()
    
    for i in best_clique:
        neigh = get_neighbours(i, nodes, adj_matrix)
        for j in best_clique:
            if i != j and j not in neigh:
                print("Unconnected vertices in the clique\n")
                sys.exit()
    return True

def ClearClique():
    global Q_BORDER, C_BORDER
    Q_BORDER = 0
    C_BORDER = 0