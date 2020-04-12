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
		r /= np.linalg.norm(r, axis=0)
		
		return np.matmul(r,V)>0


	def deter_rounding_vector(self,method='standard',search_space=50):
		#Watch proof, and check how to enumerate all posibilities of 
		#normal distrib with specific rand gen
		np.random.seed(45)
		
		V = self.sdp_solve(method=method)
		N = len(V)
		r = np.random.normal(0,1,N)
		if np.allclose(self.matrix, np.tril(self.matrix)) or np.allclose(self.matrix, np.triu(self.matrix)):
			A = self.matrix+self.matrix.T
		else: 
			A = self.matrix
		for coord in range(N):
			result2 = []
			search = np.array((np.linspace(-1,1,search_space),np.array(r[coord])))
			for value in :
				r[coord] = value
				M = np.matmul(r,V)>0		
				S = [i for i in range(len(M)) if M[i]]
				T = [vertex for vertex in self.vertices if vertex not in S]
				result2.append(np.sum(A[S,:][:,T]))
			r[coord] = list(search)[np.argmax(result2)]
		return np.matmul(r,V)>0

	def solve(self,method='standard',random=1):
		if random: M = self.proba_rounding_vector(method=method)
		else: M = self.deter_rounding_vector()
		S = [i for i in range(len(M)) if M[i]]
		T = [vertex for vertex in self.vertices if vertex not in S]
		

		# check if upper triangular or lower triangular because some formats of graphs give upper/lower only
		if np.allclose(self.matrix, np.tril(self.matrix)) or np.allclose(self.matrix, np.triu(self.matrix)):
			A = self.matrix+self.matrix.T
			return np.sum(A[S,:][:,T])
		else: return np.sum(self.matrix[S,:][:,T])

