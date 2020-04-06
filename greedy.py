import numpy as np


class Greedy:

	def __init__(self,coeff_matrix,vertices):
		self.coeff_matrix = coeff_matrix
		self.vertices = vertices
		
	def associate(self):
		S = []
		assigned = []
		dummy = self.coeff_matrix.copy()
		#print(dummy)
		while len(assigned) < len(self.vertices):
			#print(np.argmax(dummy))
			(i,j) = np.argmax(dummy)//len(self.coeff_matrix), np.argmax(dummy)%len(self.coeff_matrix)
			#print(i,j)
			if dummy[i,j] == 0: break
			if i in assigned:
				if i not in S: 
					S.append(j)
					assigned.append(j)
			elif j in assigned:
				if j not in S: 
					S.append(i)
					assigned.append(i)
			else: 
				S.append(min(i,j))
				assigned.append(i)
				assigned.append(j)
			dummy[i,j] = 0
		return S

	def weight_calculate(self,S):
		#print(S)
		T = [vertex for vertex in self.vertices if vertex not in S]
		#print(T)
		return np.sum(self.coeff_matrix[S,:][:,T])

	def solve(self):
		S = self.associate()
		return self.weight_calculate(S)



