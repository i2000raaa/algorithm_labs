import numpy as np

def read_graph_from_file(graph_str):
    file1 = open(graph_str, 'r') 
    Lines = file1.readlines() 

    adj_matrix = np.array([])

    for i in range(len(Lines)):
        chars = Lines[i].split()
        char = chars[0]
        if(char == 'c'):
            continue
        if(char == 'p'):
            graph_info = [int(s) for s in chars if s.isdigit()]
            nodes = graph_info[0]
            edges = graph_info[1]
            print("Nodes", nodes, "edges", edges)
            adj_matrix = np.zeros( (nodes, nodes) )
        else:
            graph_info = [int(s) for s in Lines[i].split() if s.isdigit()]
            adj_matrix[graph_info[0] - 1][graph_info[1] - 1] = 1
            adj_matrix[graph_info[1] - 1][graph_info[0] - 1] = 1
    return({'adj_matrix': adj_matrix, 'nodes': nodes})