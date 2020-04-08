import numpy as np


class Greedy:

	def __init__(self,coeff_matrix,vertices):
		self.coeff_matrix = coeff_matrix
		self.vertices = vertices
		
		#getting the edges
		self.edges = []
		for row in range(len(coeff_matrix)):
			for col in range(row+1,len(coeff_matrix)):
				if self.coeff_matrix[row,col] != 0: self.edges.append([self.coeff_matrix[row,col],row,col])


	def associate(self):
		S = []
		assigned = []
		dummy = self.coeff_matrix.copy()
		#sort the edge sets by weight
		self.edges = sorted(self.edges ,key = lambda x: x[0],reverse=True)
		#print(self.edges)
		for item in self.edges:
			_,i,j = item
		
			if i in assigned and j in assigned: break
			elif i in assigned: 
				if i not in S: S.append(j)
				assigned.append(j)
			elif j in assigned:
				if j not in S: S.append(i)
				assigned.append(i)
			else:
				# heuristic here, we always put the smaller index in S when we have to pick
				S.append(min(i,j))
				assigned.append(i)
				assigned.append(j)

		return S

	def weight_calculate(self,S):
		#print(S)
		T = [vertex for vertex in self.vertices if vertex not in S]
		#print(T)
		return np.sum(self.coeff_matrix[S,:][:,T])

	def solve(self):
		S = self.associate()
		return self.weight_calculate(S)



