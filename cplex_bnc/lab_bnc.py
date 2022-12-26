import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import time
from utils import read_graph
import numpy as np
import networkx as nx
import random
from docplex.mp.linear import Var
import math
from docplex.mp.model import Model

global NODES, NX_GRAPH, ADJ_MATRIX, INITIAL_SOLUTION, INITIAL_SOLUTION_VERS,  NX_COMPL_GRAPH, WEIGHTS
global UPPER_BOUND, BEST_SOLUTION_VERS, BEST_SOLUTION
global IND_SETS, MODEL, VARS, VARS_NAMES, BRANCHES_NUM
global START_TIME, EPS, GRAPH_FILE, RESULT_FILE
global ITTERATION_NUM, PREVIOUS_SOLUTION, CONSTR_LIST

def get_sorted_neigh_list(): #вершины отсортированные по степени
    global NODES, NX_GRAPH

    sorted_nodes =  sorted(NX_GRAPH, key=lambda x: len(NX_GRAPH[x]), reverse=True)
    return sorted_nodes

def get_connected_vertices(node, nodes_list): #из списка вершин выбрать соседей для "node"
    global NX_GRAPH

    new_list = []
    for node1 in nodes_list:
        if node1 in list(NX_GRAPH.neighbors(node)):
            new_list.append(node1)
    return new_list

def get_sort_list(nodes): #отсортируем вершины в порядке убывания, разделим вес на степень вершины
    global WEIGHTS, NX_COMPL_GRAPH

    sorted_nodes =  sorted(nodes, key=lambda x: WEIGHTS[x]/len(NX_GRAPH[x]), reverse=True)
    return sorted_nodes

def get_unconnected_vertices(node, nodes_list): #из списка вершин выбрать несоседей, считаем через соседей для дополнения графа
    global NX_COMPL_GRAPH

    new_list = []
    for node1 in nodes_list:
        if node1 in list(NX_COMPL_GRAPH.neighbors(node)):
            new_list.append(node1)
    return new_list

def max_clique_search():
    global NODES, NX_GRAPH

    clique_winner = []
    sorted_nodes = get_sorted_neigh_list()
    #for i in range(1000): #для больших графов
    for i in range(NODES*50):
        length_of_random = int(0.2*NODES) 
        start_ver = random.choice(sorted_nodes[:length_of_random])
        candidates = list(NX_GRAPH.neighbors(start_ver))
        tmp_clique = []
        tmp_clique.append(start_ver)
        while(len(candidates) != 0):
            node = random.choice(candidates)
            tmp_clique.append(node)
            candidates = get_connected_vertices(node, candidates)
        if len(tmp_clique) > len(clique_winner):
            clique_winner = tmp_clique
    return clique_winner

def get_max_clique_initial_solution(): #Initial solution. Чаще всего находит сразу
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

def get_ind_sets(): #дает независимые множества, основанные на раскраске графа несколькими стратегиями
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
    global NODES, MODEL, VARS, VARS_NAMES, IND_SETS, ADJ_MATRIX, CONSTR_LIST

    vars = range(NODES)
    MODEL.continuous_var_list(vars)
    VARS_NAMES = [vars.name for vars in MODEL.iter_variables()]
    #print("vars_names", VARS_NAMES)
    VARS = [vars for vars in MODEL.iter_variables()]
    #print("vars", VARS)
    MODEL.maximize(MODEL.sum(VARS))
    for i in range(NODES): #ограничение на каждую переменную
        MODEL.add_constraint(VARS[i] <= 1)
    for i in range(len(IND_SETS)): #ограничение на независимые множества
        IND_SETS[i].sort()         #чтобы избежать повторения ограничений в CONSTR_LIST     
        MODEL.add_constraint(sum(VARS[j] for j in IND_SETS[i]) <= 1 )
        CONSTR_LIST.append(IND_SETS[i])
    for i in range(NODES):
        for j in range(NODES): #ограничения на попарно несмежные вершины
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
    return {'solution_dict': solution_dict, 
            'objective_value': solution.objective_value}

def check_is_another_constr(solution):
    global CONSTR_LIST

    is_another = False
    for constraint in CONSTR_LIST:
        if(len(constraint) == len(solution)):
            for j in range(len(solution)):
                if(constraint[j] != solution[j]): 
                    is_another = True
                    break
    return is_another

def ind_sets_search(solution):
    global NODES, WEIGHTS, NX_COMPL_GRAPH

    solution_nodes = [int(i) for i in solution.get("solution_dict").keys()]
    winner_set_d = []
    winner_weight_d = 0
    weigh_deg_ver = get_sort_list(solution_nodes)
    for i in range(5):
        length_of_random = int(0.25*len(weigh_deg_ver))
        start_ver_d = random.choice(weigh_deg_ver[:length_of_random])
        candidates = list(NX_COMPL_GRAPH.neighbors(start_ver_d)) #несоседи через дополнение графа
        tmp_set_d = []
        tmp_weight_d = 0
        tmp_set_d.append(start_ver_d)
        tmp_weight_d += WEIGHTS[start_ver_d]
        while(len(candidates) != 0):
            node = random.choice(candidates)
            tmp_set_d.append(node)
            tmp_weight_d += WEIGHTS[start_ver_d]
            candidates = get_unconnected_vertices(node, candidates)
        if check_is_another_constr(tmp_set_d) and tmp_weight_d > winner_weight_d:
            winner_set_d = tmp_set_d
            winner_weight_d = tmp_weight_d
    return {'constraints': winner_set_d,
            'winner_weight': winner_weight_d
            }

def delete_slacks(number_of_constr):
    global MODEL

    constrs_list = []
    for i in range(number_of_constr):
        constr = MODEL.get_constraint_by_index(i)
        if(type(constr.get_left_expr()) != Var and constr is not None): #исключаем ограничения, где слева стоит переменная
            constrs_list.append(constr)
    slack_val = MODEL.slack_values(constrs_list)
    remove_constrs = []
    for i in range(len(constrs_list)):
        if(slack_val[i] > 0):
            remove_constrs.append(constrs_list[i])
    MODEL.remove_constraints(remove_constrs)

def add_constrs(constraints): #добавить в ограничения независимое множество 
    global MODEL, VARS

    for i in range(len(constraints)): 
        MODEL.add_constraint(sum(VARS[j] for j in constraints) <= 1 )

def check(clique):
    global NODES, NX_GRAPH

    constrs_list = []
    for i in clique:
        neigh = list(NX_GRAPH.neighbors(i))
        for j in clique:
            if i != j and j not in neigh:   #если в решении есть несоседи
                constrs_list.append([i, j])
    if(len(constrs_list) != 0):
        return ({
            "acceptable_solution": False,
            "constraints": constrs_list
        })
    return ({
        "acceptable_solution": True
     })

def get_rand_nonint_var(solution):
    global EPS

    solution_keys = solution.keys()
    min_var_key = -10
    min_var_diff = 50000
    for key in solution_keys: #ближайшие к 1 или к 0
        if (solution.get(key) - EPS) >= np.round(solution.get(key)) or (solution.get(key) + EPS) <= np.round(solution.get(key)):
            if (solution.get(key) - min_var_diff) < np.round(solution.get(key)) or (solution.get(key) + min_var_diff) > np.round(solution.get(key)):
                min_var_diff = abs(solution.get(key) - 1)
                min_var_key = key
    return {'vars_name': min_var_key,
            'vars_val': solution.get(min_var_key),
            'is_integer': False}

def check_is_integer(solution_dict): #проверяем решение на целочисленность
    global EPS

    keys = solution_dict.keys()
    for key in keys:
        if (solution_dict.get(key) - EPS) >= np.round(solution_dict.get(key)) or (solution_dict.get(key) + EPS) <= np.round(solution_dict.get(key)):
            return {'vars_name': key,
                    'vars_val': solution_dict.get(key),
                    'is_integer': False}
    return {'is_integer': True}

def branch_and_cut():
    global BEST_SOLUTION
    global BEST_SOLUTION_VERS
    global CONSTR_LIST
    global BRANCHES_NUM
    global PREVIOUS_SOLUTION
    global START_TIME
    global ITTERATION_NUM

    solution = solve_problem()                    #S=solve(M)
    end = time.time()
    if(end - START_TIME> 7200):
        print("Time limit")
        return
    if(solution is not None):
        upper_bound = math.floor(solution.get("objective_value"))
        if(upper_bound <= BEST_SOLUTION):          #if ([f(S)] <= f*)
            return
        else:
            constraints = ind_sets_search(solution)
            while(constraints):                         #while (C=separation(S, M)):
                constraint = constraints.get("constraints")
                constraint.sort()                       #чтобы избежать повторения накладываемых ограничений
                if(check_is_another_constr(constraint)):
                    CONSTR_LIST.append(constraint)  
                    add_constrs(constraint)      #M = M.add_constraint(C)
                    ITTERATION_NUM += 1
                    PREVIOUS_SOLUTION = solution.get("objective_value")    #предыдущее решение
                    solution = solve_problem()                          #S = solve(M)
                    if(solution is not None):
                        upper_bound = math.floor(solution.get("objective_value"))
                        if(upper_bound <= BEST_SOLUTION):       #if ([f(S)] <= f*)
                            return
                        if ITTERATION_NUM == 50 and (abs(math.floor(solution.get("objective_value")) - PREVIOUS_SOLUTION) <= 0.5): 
                            print("Itteration_num worked!")
                            break   #Tailing off
                else:
                    break
        check_int = check_is_integer(solution.get("solution_dict"))
        if not check_int.get("is_integer"): #fractional solution
            i = random.randint(0, 1)                                        #branching
            answer = get_rand_nonint_var(solution.get("solution_dict"))
            name = answer.get('vars_name')
            value = answer.get('vars_val')
            if(i):   
                BRANCHES_NUM += 1
                current_branch = BRANCHES_NUM
                MODEL.add_constraint(VARS[int(name)] <= math.floor(value), str(current_branch))
                branch_and_cut()
                MODEL.remove_constraint(str(current_branch))
                BRANCHES_NUM += 1
                current_branch = BRANCHES_NUM
                MODEL.add_constraint(VARS[int(name)] >= math.ceil(value), str(current_branch))
                branch_and_cut()
                MODEL.remove_constraint(str(current_branch))
            else:
                BRANCHES_NUM += 1
                current_branch = BRANCHES_NUM
                MODEL.add_constraint(VARS[int(name)] >= math.ceil(value), str(current_branch))
                branch_and_cut()
                MODEL.remove_constraint(str(current_branch))
                BRANCHES_NUM += 1
                current_branch = BRANCHES_NUM
                MODEL.add_constraint(VARS[int(name)] <= math.floor(value), str(current_branch))
                branch_and_cut()
                MODEL.remove_constraint(str(current_branch))            
        else:       #integer solution
            ans = check([ int(v) for v in solution.get("solution_dict")])
            if(ans.get("acceptable_solution") == False):
                for constraint in ans.get("constraints"):
                    constraint.sort()
                    if(check_is_another_constr(constraint)):
                        CONSTR_LIST.append(constraint)
                        add_constrs(constraint)  #M = M.add_constraint(C)
                        branch_and_cut()
            else:
                upper_bound = math.floor(solution.get("objective_value"))
                print("New integer solution : ", upper_bound)
                if(upper_bound >= BEST_SOLUTION):           
                    # i = random.randint(0, 1)
                    # if(i):
                    if(random.randint(0, 1000) < 350):
                        print("Slack values deleted")
                        delete_slacks(MODEL.number_of_constraints)        #remove slacks
                    best_solution_answers = []
                    for key in solution.get("solution_dict").keys():
                        best_solution_answers.append(key)
                    BEST_SOLUTION = upper_bound
                    BEST_SOLUTION_VERS = best_solution_answers
                    return
                else:
                    return
    else:
        return
    return

graph_list = ["brock200_1.clq", "brock200_2.clq", "brock200_3.clq", "brock200_4.clq", 
"c-fat200-1.clq", "c-fat200-2.clq", "c-fat200-5.clq", "c-fat500-1.clq", "c-fat500-2.clq",
"c-fat500-5.clq", "c-fat500-10.clq", "C125.9.clq", "gen200_p0.9_44.clq", "gen200_p0.9_55.clq",
"johnson8-2-4.clq", "johnson8-4-4.clq", "johnson16-2-4.clq",
"hamming6-2.clq", "hamming6-4.clq", "hamming8-2.clq", "hamming8-4.clq", 
"keller4.clq", "MANN_a9.clq", "MANN_a27.clq", "MANN_a45.clq", 
"p_hat300-1.clq", "p_hat300-2.clq", "p_hat300-3.clq",
"san200_0.7_1.clq", "san200_0.7_2.clq", "san200_0.9_1.clq", "san200_0.9_2.clq", "san200_0.9_3.clq", "sanr200_0.7.clq"]

hard_list = ["brock200_1.clq", "brock200_2.clq", "brock200_3.clq", "brock200_4.clq", "C125.9.clq", 
"gen200_p0.9_44.clq", "keller4.clq", "MANN_a27.clq",  
"p_hat300-1.clq", "p_hat300-2.clq", "p_hat300-3.clq"]
very_hard_list = ["MANN_a45.clq"]

test_list = ["c-fat200-1.clq", "c-fat200-2.clq", "c-fat200-5.clq", "c-fat500-1.clq", "c-fat500-2.clq",
"c-fat500-5.clq", "c-fat500-10.clq", "gen200_p0.9_55.clq",
"johnson8-2-4.clq", "johnson8-4-4.clq", "johnson16-2-4.clq",
"hamming6-2.clq", "hamming6-4.clq", "hamming8-2.clq", "hamming8-4.clq", "MANN_a9.clq",
"san200_0.7_1.clq", "san200_0.9_1.clq", "san200_0.9_2.clq"]


CONSTR_LIST = []            #глобальный список ограничений, чтобы проверять их на повторения
#EPS = 10e-6
EPS = 1e-6 
RESULT_FILE = "bnc_results.txt"

for graph_file in graph_list:
    GRAPH_FILE = graph_file
    print("Instance:", GRAPH_FILE)

    GRAPH = read_graph.read_graph_from_file(GRAPH_FILE) #read_graph
    ADJ_MATRIX = GRAPH.get("adj_matrix")                #adjacency matrix
    NODES = GRAPH.get("nodes")                          #number of nodes
    WEIGHTS = [np.ceil(10 * i / NODES) * 0.1 for i in range(1, NODES + 1)] #giving weights
    NX_GRAPH =  nx.from_numpy_matrix(ADJ_MATRIX)        #graph from matrix
    NX_COMPL_GRAPH = nx.complement(NX_GRAPH)            #complement of graph NX_GRAPH

    INITIAL_SOLUTION_VERS = get_max_clique_initial_solution()              #with randomization
    INITIAL_SOLUTION = len(INITIAL_SOLUTION_VERS)
    BEST_SOLUTION_VERS = INITIAL_SOLUTION_VERS
    BEST_SOLUTION = INITIAL_SOLUTION

    IND_SETS = get_ind_sets()
    MODEL = Model("model")      #CPLEX model

    get_problem() 
    solution = solve_problem()
    UPPER_BOUND = math.floor(solution.get("objective_value"))
    print("CPLEX BnC upper bound", UPPER_BOUND)

    BRANCHES_NUM = 0 
    ITTERATION_NUM = 0
    PREVIOUS_SOLUTION = BEST_SOLUTION
    START_TIME = time.time()
    sol = branch_and_cut()
    end_time = time.time()
    print(end_time-START_TIME)
    file = open(r''+RESULT_FILE+'',"a")
    file.write("BnC solution:" + GRAPH_FILE + " Clique size: " + str(BEST_SOLUTION) + " Time: " + str(end_time-START_TIME) + " sec " + " Clique vertices: " + str(BEST_SOLUTION_VERS) + "\n")
    file.close()

    check_sol = check([int(v) for v in BEST_SOLUTION_VERS])
    print("CPLEX BnC Clique vertices:", BEST_SOLUTION_VERS)
    print("CPLEX BnC Clique size:", str(BEST_SOLUTION))
    print("CPLEX BnC Checker:", check_sol.get("acceptable_solution"))
    print("__________________________________________________________")
