import numpy as np
import math

"""
We are simply reading graphs from already generated text files, and will simply return them as a
adj_matrix to be used
"""


def graph_read(path_to_file):
	with open(path_to_file,'r') as f:
		lines = f.readlines()
		for idx,line in enumerate(lines,start=0):
			if idx == 0: 
				n,m = int(line.split()[0].strip()), int(line.split()[1].strip())
				X = np.zeros((n,n))
			else:
				v1, v2, w = int(line.split()[0].strip()), int(line.split()[1].strip()), int(line.split()[2].strip())
				X[v1-1,v2-1] = w
	return X,n,m
