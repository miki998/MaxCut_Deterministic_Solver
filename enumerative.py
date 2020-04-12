import numpy as np 
from itertools import combinations 
from tqdm import tqdm

class Enumerative:

	def __init__(self,coeff_matrix,vertices):
		self.coeff_matrix = coeff_matrix
		self.vertices = vertices

	def enumerate(self,cutoff=3): #outputs all the combinasions for S set and else is in V/S

		possible_arrays = []
		for i in range(1,len(self.vertices)):
			if i > cutoff: return possible_arrays #heuristic of stopping and we look max from here
			possible_arrays = possible_arrays + list(combinations(self.vertices, i))
		#print(possible_arrays)
		return possible_arrays

	def weight_calculate(self,S):

		T = [vertex for vertex in self.vertices if vertex not in S]
		return np.sum(self.coeff_matrix[S,:][:,T])


	def solve(self,cutoff=3):

		possible_arrays = self.enumerate(cutoff)
		#Sm = (54, 59)
		#self.weight_calculate(Sm)
		
		return max([self.weight_calculate(S) for S in possible_arrays])
