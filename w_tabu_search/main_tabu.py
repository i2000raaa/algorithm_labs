import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import read_graph
from max_clique import max_clique
#import tabu_read_graph
import tabu_max_clique
import time
import csv

print("Start!")
easy_test_list = ["examples/C125.9.clq", 
"examples/johnson8-2-4.clq", 
"examples/johnson16-2-4.clq", 
"examples/MANN_a9.clq",
"examples/keller4.clq",
"examples/hamming8-4.clq"
]
medium_test_list = ["examples/brock200_1.clq", 
"examples/brock200_2.clq", 
"examples/brock200_3.clq", 
"examples/brock200_4.clq",
"examples/gen200_p0.9_44.clq",
"examples/gen200_p0.9_55.clq",
"examples/MANN_a27.clq",
"examples/p_hat1000-1.clq",
"examples/p_hat1000-2.clq",
"examples/p_hat300-3.clq",
"examples/p_hat500-3.clq",
"examples/sanr200_0.9.clq",
"examples/sanr400_0.7.clq"
]
hard_test_list = ["examples/brock400_1.clq", 
"examples/brock400_2.clq", 
"examples/brock400_3.clq",
"examples/brock400_4.clq",
"examples/san1000.clq",
"examples/p_hat1500-1.clq"
]
graph_list = ["examples/brock200_1.clq", 
"examples/brock200_2.clq", 
"examples/brock200_3.clq", 
"examples/brock200_4.clq", 
"examples/brock400_1.clq", 
"examples/brock400_2.clq", 
"examples/brock400_3.clq",
"examples/brock400_4.clq",
"examples/C125.9.clq",
"examples/gen200_p0.9_44.clq",
"examples/gen200_p0.9_55.clq",
"examples/hamming8-4.clq",
"examples/johnson16-2-4.clq",
"examples/johnson8-2-4.clq",
"examples/keller4.clq",
"examples/MANN_a27.clq",
"examples/MANN_a9.clq",
"examples/p_hat1000-1.clq",
"examples/p_hat1000-2.clq",
"examples/p_hat1500-1.clq",
"examples/p_hat300-3.clq",
"examples/p_hat500-3.clq",
"examples/san1000.clq",
"examples/sanr200_0.9.clq",
"examples/sanr400_0.7.clq"]

with open("tabu_max_clique.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter = "/", lineterminator="\r")
    file_writer.writerow(["Instance  ", "Time, sec  ", "Clique size  ", "Clique vertices  "])
    for graph_file in graph_list:
        GRAPH = read_graph.read_graph_from_file(graph_file)
        NODES = GRAPH.get("nodes")
        ADJ_MATRIX = GRAPH.get("adj_matrix")
        start_time = time.time()
        BEST_CLIQUE = tabu_max_clique.RunSearch(5, NODES, ADJ_MATRIX, NODES)
        end_time = time.time()
        CLIQUE_SIZE = len(tabu_max_clique.BEST_CLIQUE)
        file_writer.writerow([graph_file, round(end_time - start_time, 3), CLIQUE_SIZE, "\n"])


        print("Instance:", graph_file)
        print("Time:", round(end_time - start_time, 1), "seconds")
        print("Clique size:", CLIQUE_SIZE)
        print("Checker:", tabu_max_clique.check(NODES, BEST_CLIQUE, ADJ_MATRIX))
        tabu_max_clique.BEST_CLIQUE.clear()
        print("__________________________________________________________")
w_file.close()