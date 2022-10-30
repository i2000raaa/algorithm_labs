import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from utils import read_graph
import vertex_coloring
import time
import csv
import networkx as nx

print("Start!")

test_list = ["examples/anna.col.txt", 
"examples/huck.col.txt", 
"examples/jean.col.txt", 
"examples/inithx.i.1.col", 
"examples/latin_square_10.col.txt",
"examples/mulsol.i.1.col",
"examples/school1_nsh.col.txt",
"examples/school1.col.txt",
"examples/myciel3.col.txt",
"examples/myciel7.col.txt"]
graph_list = ["examples/myciel3.col.txt",
"examples/myciel7.col.txt",
"examples/school1_nsh.col.txt",
"examples/school1.col.txt",
"examples/anna.col.txt",
"examples/miles1000.col.txt",
"examples/miles1500.col.txt",
"examples/le450_5a.col.txt",
"examples/le450_15b.col.txt",
"examples/queen11_11.col.txt"]


with open("Vertex_coloring.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter = ",", lineterminator="\r")
    file_writer.writerow(["Instance  ", "Time, sec  ", "Colors  ", "Color classes  "])
    for graph_file in graph_list:
        GRAPH = read_graph.read_graph_from_file(graph_file)
        NODES = GRAPH.get("nodes")
        ADJ_MATRIX = GRAPH.get("adj_matrix")
        G = nx.from_numpy_matrix(ADJ_MATRIX)
        start_time = time.time()
        vertex_coloring.graph_coloring(NODES, ADJ_MATRIX)
        end_time = time.time()
        file_writer.writerow([graph_file, round(end_time - start_time, 3),  vertex_coloring.COLOR_CNT + 1, vertex_coloring.swap_dict(vertex_coloring.GRAPH_COLORING).values(), "\n"])


        print("Instance:", graph_file)
        print("Time:", round(end_time - start_time, 1), "seconds")
        print("Colors:  ", vertex_coloring.COLOR_CNT + 1)
        print("Checker:", vertex_coloring.check(NODES, vertex_coloring.GRAPH_COLORING, ADJ_MATRIX))
        print("__________________________________________________________")
w_file.close()