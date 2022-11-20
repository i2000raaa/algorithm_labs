import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import time
from utils import read_graph
import numpy as np
import networkx as nx
import random
from collections import Counter
import math
from docplex.mp.model import Model

global NODES, NX_GRAPH, ADJ_MATRIX, INITIAL_SOLUTION, INITIAL_SOLUTION_VERS
global UPPER_BOUND, BEST_SOLUTION_VERS, BEST_SOLUTION
global IND_SETS, MODEL, VARS, VARS_NAMES, BRANCHES_NUM
global START_TIME, EPS, GRAPH_FILE, RESULT_FILE

def get_neighbours(node):
    global NODES, ADJ_MATRIX
    return [i for i in range(NODES) if ADJ_MATRIX[node][i] == 1]

def get_neigh_dict():
    global NODES
    dict_nodes = {}
    for node in range(NODES):
        dict_nodes[node] = get_neighbours(node)
    sorted_nodes = {k: v for k, v in sorted(dict_nodes.items(), key=lambda item: len(item[1]), reverse=True)}
    return sorted_nodes

def get_connected_vertices(node, ver_list):
    global ADJ_MATRIX
    new_list = []
    for node1 in ver_list:
        if (ADJ_MATRIX[node1][node] == 1):
            new_list.append(node1)
    return new_list

def max_clique_search():
    global NODES
    clique_winner = []
    sorted_nodes = get_neigh_dict()
    #for i in range(1000):
    for i in range(NODES*50):
        length_of_random = int(0.2*NODES) 
        start_ver = random.choice(list(sorted_nodes.keys())[:length_of_random])
        candidates = get_neighbours(start_ver)
        tmp_clique = []
        tmp_clique.append(start_ver)
        while(len(candidates) != 0):
            node = random.choice(candidates)
            tmp_clique.append(node)
            candidates = get_connected_vertices(node, candidates)
        if len(tmp_clique) > len(clique_winner):
            clique_winner = tmp_clique
    return clique_winner

def get_max_clique_initial_solution(): #gives Initial solution
    global RESULT_FILE, GRAPH_FILE
    start_time = time.time()
    solution = max_clique_search()
    end_time = time.time()
    file = open(r''+str(RESULT_FILE)+'',"a")
    file.write(" Initial solution: " + GRAPH_FILE + " Clique size "  + str(len(solution)) + " Heuristic time: " + str(end_time-start_time) + " sec " + " Clique vertices: " + str(solution) + "\n")
    file.close()
    print("Initial solution: ", len(solution), " Heuristic time: ", str(end_time-start_time), " sec ")
    print("Initial solution vertices ", solution)
    return solution

def get_ind_sets(): #gives independent sets based on graph coloring by several strategies
    global NX_GRAPH
    ind_sets = []
    strategies = [nx.coloring.strategy_random_sequential,
                nx.coloring.strategy_largest_first,
                nx.coloring.strategy_saturation_largest_first,
                nx.coloring.strategy_independent_set,
                nx.coloring.strategy_connected_sequential_dfs,
                nx.coloring.strategy_connected_sequential_bfs,
                nx.coloring.strategy_smallest_last]
    for strategy in strategies:
        colored_graph = nx.coloring.greedy_color(NX_GRAPH, strategy=strategy)
        for color in set(color for ver, color in colored_graph.items()):
            ind_sets.append(
                [k for k, v in colored_graph.items() if v == color])
    return ind_sets

def get_problem():
    global NODES, MODEL, VARS, VARS_NAMES, IND_SETS
    vars = range(NODES)
    MODEL.continuous_var_list(vars)
    VARS_NAMES = [vars.name for vars in MODEL.iter_variables()]
    #print("vars_names", VARS_NAMES)
    VARS = [vars for vars in MODEL.iter_variables()]
    #print("vars", VARS)
    MODEL.maximize(MODEL.sum(VARS))
    for i in range(len(IND_SETS)): 
        MODEL.add_constraint(sum(VARS[j] for j in IND_SETS[i]) <= 1 )
    for i in range(NODES):
        for j in range(NODES):
            if(i != j and ADJ_MATRIX[i][j] == 0):
                MODEL.add_constraint(VARS[i] + VARS[j] <= 1)
    
def solve_problem():
    global MODEL, VARS, VARS_NAMES
    solution = MODEL.solve(log_output=False)
    vars_val = [solution.get_value(v) for v in VARS] 
    solution_dict = {}
    for i in range(len(VARS_NAMES)):
        if vars_val[i] > 0:
             solution_dict[str(VARS_NAMES[i])] = vars_val[i]
    return {'solution': solution_dict, 
            'objective_value': solution.objective_value}

def check_is_integer(solution):
    global EPS
    keys = solution.keys()
    for key in keys:
        if (solution.get(key) - EPS) >= np.round(solution.get(key)) or (solution.get(key) + EPS) <= np.round(solution.get(key)):
            return {'vars_name': key,
                    'vars_val': solution.get(key),
                    'is_integer': False}
    return {'is_integer': True}

def get_random_non_int_var(solution):
    global EPS
    solution_keys = solution.keys()
    min_key = -10
    min_diff = 50000
    for key in solution_keys: #close to 1 or 0
        if (solution.get(key) - EPS) >= np.round(solution.get(key)) or (solution.get(key) + EPS) <= np.round(solution.get(key)):
            if (solution.get(key) - min_diff) < np.round(solution.get(key)) or (solution.get(key) + min_diff) > np.round(solution.get(key)):
                min_diff = abs(solution.get(key) - 1)
                min_key = key
    return {'vars_name': min_key,
            'vars_val': solution.get(min_key),
            'is_integer': False}

def branch_and_bound():
    global START_TIME, BEST_SOLUTION, BEST_SOLUTION_VERS, BRANCHES_NUM
    end_time = time.time()
    if(end_time - START_TIME > 7200): 
        print("Interrupted")
        return
    solution = solve_problem()
    if(solution is not None):
        upper_bound = math.floor(solution.get("objective_value"))
        answer = check_is_integer(solution.get("solution"))
        if(answer.get('is_integer')):
            current_objective_value = round(solution.get("objective_value"))
            if(BEST_SOLUTION < current_objective_value): #current solution better than previous
                end_time = time.time()
                print("Current best solution", current_objective_value, "Time: ", end_time - START_TIME, " sec")
                current_solution = []
                for key in solution.get("solution").keys():
                    current_solution.append(key)
                BEST_SOLUTION = current_objective_value
                BEST_SOLUTION_VERS = current_solution
            return solution
        else:
            if(BEST_SOLUTION >= upper_bound): 
                return
            else:                           
                i = random.randint(0, 1)
                answer = get_random_non_int_var(solution.get("solution"))
                name = answer.get('vars_name')
                value = answer.get('vars_val')
                if(i):   
                    BRANCHES_NUM = BRANCHES_NUM + 1
                    current_branch = BRANCHES_NUM
                    MODEL.add_constraint(VARS[int(name)] <= math.floor(value), str(current_branch))
                    branch_and_bound()
                    MODEL.remove_constraint(str(current_branch))
                    BRANCHES_NUM = BRANCHES_NUM + 1
                    current_branch = BRANCHES_NUM
                    MODEL.add_constraint(VARS[int(name)] >= math.ceil(value), str(current_branch))
                    branch_and_bound()
                    MODEL.remove_constraint(str(current_branch))
                else:
                    BRANCHES_NUM = BRANCHES_NUM + 1
                    current_branch = BRANCHES_NUM
                    MODEL.add_constraint(VARS[int(name)] >= math.ceil(value), str(current_branch))
                    branch_and_bound()
                    MODEL.remove_constraint(str(current_branch))
                    BRANCHES_NUM = BRANCHES_NUM + 1
                    current_branch = BRANCHES_NUM
                    MODEL.add_constraint(VARS[int(name)] <= math.floor(value), str(current_branch))
                    branch_and_bound()
                    MODEL.remove_constraint(str(current_branch))             
    else:
        return

def check(clique_winner):
    global NODES, ADJ_MATRIX
    counter = Counter(clique_winner)

    if sum(counter.values()) > len(counter):
        print("Duplicates in the clique\n")
        sys.exit()
    for i in clique_winner:
        neigh = get_neighbours(i)
        for j in clique_winner:
            if i != j and j not in neigh:
                print("Unconnected vertices in the clique\n")
                sys.exit()
    return True

graph_list = ["brock200_1.clq", "brock200_2.clq", "brock200_3.clq", "brock200_4.clq", 
"c-fat200-1.clq", "c-fat200-2.clq", "c-fat200-5.clq", "c-fat500-1.clq", "c-fat500-2.clq",
"c-fat500-5.clq", "c-fat500-10.clq", "C125.9.clq", "gen200_p0.9_44.clq", "gen200_p0.9_55.clq",
"johnson8-2-4.clq", "johnson8-4-4.clq", "johnson16-2-4.clq",
"hamming6-2.clq", "hamming6-4.clq", "hamming8-2.clq", "hamming8-4.clq", 
"keller4.clq", "MANN_a9.clq", "MANN_a27.clq", "MANN_a45.clq", 
"p_hat300-1.clq", "p_hat300-2.clq", "p_hat300-3.clq",
"san200_0.7_1.clq", "san200_0.7_2.clq", "san200_0.9_1.clq", "san200_0.9_2.clq", "san200_0.9_3.clq", "sanr200_0.7.clq"]

EPS = 10e-6 
RESULT_FILE = "cplex_best_results.txt"

for graph_file in graph_list:
    GRAPH_FILE = graph_file
    print("Instance:", GRAPH_FILE)

    GRAPH = read_graph.read_graph_from_file(GRAPH_FILE) #read_graph
    ADJ_MATRIX = GRAPH.get("adj_matrix") #adjacency matrix
    NODES = GRAPH.get("nodes") #number of nodes
    NX_GRAPH =  nx.from_numpy_matrix(ADJ_MATRIX) #graph from matrix

    INITIAL_SOLUTION_VERS = get_max_clique_initial_solution() #with randomization
    INITIAL_SOLUTION = len(INITIAL_SOLUTION_VERS)
    
    BEST_SOLUTION_VERS = INITIAL_SOLUTION_VERS
    BEST_SOLUTION = INITIAL_SOLUTION

    IND_SETS = get_ind_sets()   #independent_sets

    MODEL = Model("model")      #CPLEX model
    get_problem()               #gives objective function, variables, constraintes 
    solution = solve_problem()

    UPPER_BOUND = math.floor(solution.get("objective_value"))
    print("CPLEX BnB upper bound", UPPER_BOUND)
    BRANCHES_NUM = 0 

    if(UPPER_BOUND > BEST_SOLUTION):
        START_TIME = time.time()
        branch_and_bound()  #recursion
        end_time = time.time()
        file = open(r''+RESULT_FILE+'',"a")
        file.write("BnB solution:" + GRAPH_FILE + " Clique size: " + str(BEST_SOLUTION) + " Time: " + str(end_time-START_TIME) + " sec " + " Clique vertices: " + str(BEST_SOLUTION_VERS) + "\n")
        file.close()
        print("CPLEX BnB time:", end_time-START_TIME, " sec ")
    print("CPLEX BnB Clique vertices:", BEST_SOLUTION_VERS)
    print("CPLEX BnB Clique size:", str(BEST_SOLUTION))
    print("CPLEX BnB Checker:", check([int(v) for v in BEST_SOLUTION_VERS]))
    print("__________________________________________________________")
