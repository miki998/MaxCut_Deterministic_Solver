#Imported libs
import numpy as np
import math
from sdp_solver import *
import cvxpy as cp

""" 

We implement here the 0.878-approx randomized algo for maxcut, we will also try to do the derandomized

"""
############################################################################

class Sdp_relax_algo:

	def __init__(self,coeff_matrix,n):
		self.matrix, self.n = coeff_matrix, n
		#print(self.matrix)
		self.X = np.diag(np.ones(n))
		for _ in range(100):
			x, y = np.random.randint(0,n-1), np.random.randint(0,n-1)
			if x==y: continue
			self.X[x,y] = 2*np.random.random()
		self.X = np.matmul(self.X,self.X.T)
		self.vertices = [i for i in range(n)]

	def sdp_solve(self,method='grad'):
		#Method of Gradient projection
		if method == 'grad':
			#print(self.matrix)
			#print(self.X_init)
			g = Grad_Proj(self.matrix,self.X)
			Y = g.solve()
		
		#Standard method, python lib CVX
		if method == 'standard':
			C = -(self.matrix+self.matrix.T)
			A = []
			b = []
			for i in range(self.n):
				tmp = 	np.zeros((self.n,self.n))
				tmp[i,i] = 1
				A.append(tmp)
				b.append(1)

			X = cp.Variable((self.n,self.n), PSD=True)
			constraints = [
				cp.trace(A[i] @ X) == b[i] for i in range(self.n)
			]			
			prob = cp.Problem(cp.Maximize(cp.trace(C @ X)),
					   constraints)
			prob.solve()

			Y = prob.solution.primal_vars[list(prob.solution.primal_vars.keys())[0]]

		return Y

	def proba_rounding_vector(self,method='standard'):

		V = self.sdp_solve(method=method) 
		N = len(V)

		# Different Random Generators for symmetrical vector
		#Gen1
		r = np.random.normal(0,1,N)

		
		return np.matmul(r,V)>0


	def deter_rounding_vector(self):
		#Watch proof, and check how to enumerate all posibilities of 
		#normal distrib with specific rand gen
		pass


	def solve(self,method='standard',random=1):
		if random: M = self.proba_rounding_vector(method=method)
		else: M = self.deter_rounding_vector()
		S = [i for i in range(len(M)) if M[i]]
		T = [vertex for vertex in self.vertices if vertex not in S]

		return (1/4)*(np.sum(self.matrix+self.matrix.T) - np.sum(self.matrix[S,:][:,T]))