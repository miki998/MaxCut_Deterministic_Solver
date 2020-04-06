#Imported libs
from math import *
import random
from graph_reader import *
""" 

We implement here the 1/2-approx randomized algo for maxcut, we will also try to do the derandomized

"""

############################################################################

class Half_rand_algo:

	def __init__(self,coeff_matrix,vertices):
		self.coeff_matrix = coeff_matrix
		self.vertices = vertices

	def solve(self):
		#input N: number of vertex , W: weights matrix
		#output U: first set, v: value of the cut

		assert self.coeff_matrix.shape[0] == len(self.vertices)
		#assert check_symmetrys(W)

		U,S = [],[]

		#just heuristic random
		for v_idx in self.vertices:

			if random.random() >= 0.5:  U.append(v_idx)
			else: S.append(v_idx)

		#print(self.coeff_matrix[U,:][:,S])

		return np.sum(self.coeff_matrix[U,:][:,S])


