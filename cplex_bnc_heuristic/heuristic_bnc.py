import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import time
from utils import read_graph
import numpy as np
import networkx as nx
import random

global NODES, NX_GRAPH, ADJ_MATRIX, NX_COMPL_GRAPH, WEIGHTS
global GRAPH_FILE, RESULT_FILE


def get_sort_list(): #отсортируем в порядке убывания, разделим вес на степень вершины
    global WEIGHTS, NX_COMPL_GRAPH, NX_GRAPH
    sorted_nodes =  sorted(NX_COMPL_GRAPH, key=lambda x: WEIGHTS[x]/len(NX_GRAPH[x]), reverse=True)
    return sorted_nodes

def get_unconnected_vertices(node, ver_list):
    global NX_COMPL_GRAPH
    new_list = []
    for node1 in ver_list:
        if node1 in list(NX_COMPL_GRAPH.neighbors(node)): #из списка вершин выбрать несоседей, считаем через соседей для дополнения графа
            new_list.append(node1)
    return new_list

def ind_sets_search():
    global NODES, WEIGHTS, NX_COMPL_GRAPH
    winner_set = []
    winner_weight = 0
    weigh_deg_vers = get_sort_list()
    for i in range(5):
        length_of_random = int(0.25*NODES)
        start_ver_d = random.choice(weigh_deg_vers[:length_of_random])
        candidates = list(NX_COMPL_GRAPH.neighbors(start_ver_d))
        tmp_set_d = []
        tmp_weight_d = 0
        tmp_set_d.append(start_ver_d)
        tmp_weight_d += WEIGHTS[start_ver_d]
        while(len(candidates) != 0):
            node = random.choice(candidates)
            tmp_set_d.append(node)
            tmp_weight_d += WEIGHTS[node]
            candidates = get_unconnected_vertices(node, candidates)
        if tmp_weight_d > winner_weight:
            winner_set = tmp_set_d
            winner_weight = tmp_weight_d
    return {'winner_set': winner_set,
            'winner_weight': winner_weight
            }

graph_list = ["brock200_1.clq", "brock200_2.clq", "brock200_3.clq", "brock200_4.clq", 
"c-fat200-1.clq", "c-fat200-2.clq", "c-fat200-5.clq", "c-fat500-1.clq", "c-fat500-2.clq",
"c-fat500-5.clq", "c-fat500-10.clq", "C125.9.clq", "gen200_p0.9_44.clq", "gen200_p0.9_55.clq",
"johnson8-2-4.clq", "johnson8-4-4.clq", "johnson16-2-4.clq",
"hamming6-2.clq", "hamming6-4.clq", "hamming8-2.clq", "hamming8-4.clq", 
"keller4.clq", "MANN_a9.clq", "MANN_a27.clq", "MANN_a45.clq", 
"p_hat300-1.clq", "p_hat300-2.clq", "p_hat300-3.clq",
"san200_0.7_1.clq", "san200_0.7_2.clq", "san200_0.9_1.clq", "san200_0.9_2.clq", "san200_0.9_3.clq", "sanr200_0.7.clq"]

RESULT_FILE = "bnc_heuristic_results_2.txt"

for graph_file in graph_list:
    GRAPH_FILE = graph_file
    print("Instance:", GRAPH_FILE)
    GRAPH = read_graph.read_graph_from_file(GRAPH_FILE) #read_graph
    ADJ_MATRIX = GRAPH.get("adj_matrix") #adjacency matrix
    NODES = GRAPH.get("nodes") #number of nodes
    WEIGHTS = [np.ceil(10 * i / NODES) * 0.1 for i in range(1, NODES + 1)] #giving weights
    NX_GRAPH =  nx.from_numpy_matrix(ADJ_MATRIX)    #graph from matrix
    #print("NX_GRAPH[1]", NX_GRAPH[1])
    #print('LEN  NX_GRAPH[1]', len(NX_GRAPH[1]))
    NX_COMPL_GRAPH = nx.complement(NX_GRAPH)        #complement of graph NX_GRAPH
    #print("NX_COMPL_GRAPH[1]", NX_COMPL_GRAPH[1])
    #print('LEN  NX_COMPL_GRAPH[1]', len(NX_COMPL_GRAPH[1]))
    start_time = time.time()
    ind_set = ind_sets_search()
    end_time = time.time()
    file = open(r''+RESULT_FILE+'',"a")
    file.write("Heuristic for bnc: " + GRAPH_FILE + " Weight: " + str(ind_set.get('winner_weight')) + " Time: " + str(end_time-start_time) + " sec " + " Set: " + str(ind_set.get('winner_set')) + "\n")
    file.close()

    def check_final(ind_set):
        global NODES, NX_COMPL_GRAPH

        for i in ind_set:
            neigh_list = list(NX_GRAPH.neighbors(i))
            for j in ind_set:
                if i != j and j in neigh_list:
                    print("Connected vertices in the independent set\n")
        return True

    print("Winner set: ", ind_set.get('winner_set'))
    print("Winner weight: ", ind_set.get('winner_weight'))
    print("Checker:", check_final(ind_set.get('winner_set')))
    print("Time: ", str(end_time-start_time))
    print("__________________________________________________________")
