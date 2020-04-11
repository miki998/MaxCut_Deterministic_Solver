import numpy as np
from scipy import linalg
from tqdm import tqdm

# IMPLEMENTATION OF DIFFERENT METHOD TO SOLVE SDP


class Grad_Proj:

	def __init__(self,coeff_matrix, x_matrix):
		# the matrix of input is representing C
		self.coeff_matrix = coeff_matrix + coeff_matrix.T
		self.x_matrix = x_matrix
		#initializations
		#lower triangle
		self.l_triangle = self.l_triangle_init()

	def objective_func(self,l_matrix):
		return np.trace(np.matmul(self.coeff_matrix,np.matmul(l_matrix,l_matrix.T)))

	def l_triangle_init(self):
		#initialization of L using Cholesky from feasible solution of X
		return linalg.cholesky(self.x_matrix, lower=True)

	def lower_keep(self, matrix):
		#keep lower triangle and replace by zero all the other number
		n = matrix.shape[0]
		lower_ones = np.tril(np.ones((n,n)),-1)
		return np.multiply(matrix, lower_ones)

	def normalize(self, l_matrix):
		for row in range(l_matrix.shape[0]):
			row_norm = np.sqrt(sum(l_matrix[row,:]**2))
			try: l_matrix[row,:] = l_matrix[row,:]/row_norm 
			except: 
				print('Division by zero')
				return None
		return l_matrix

	def gradient_step(self, l_matrix):
		#Finding the projected gradient step such that point is still feasible
		def grad_projection(g_matrix):
			projected = g_matrix.copy()
			for row in range(g_matrix.shape[0]):
				projected[row,:] -= np.dot(g_matrix[row,:],l_matrix[row,:])*l_matrix[row,:]
			return projected
		grad = 2*self.lower_keep(np.matmul(self.coeff_matrix,l_matrix))
		return grad, grad_projection(grad)

	def step_alpha(self,sig,alpha_init,l_matrix,grad,grad_proj):
		#line search, here the paper uses Armijo
		def inequality_check(alpha):
			nextL = self.normalize(l_matrix+alpha*grad_proj)
			left = self.objective_func(nextL)-self.objective_func(l_matrix)
			right = sig*alpha*np.trace(np.matmul(grad,grad_proj))
			#print(right)	
			#print(sum([grad_proj[i,i] for i in range(grad_proj.shape[0])]))
			#print(sum([np.matmul(grad,grad_proj)[i,i] for i in range(grad.shape[0])]))
			if right == 0 and left>0 and alpha < 2: return False
			#print('Trigger')
			if left < 0: return True
			return left > right
		
		alpha = alpha_init 
		while inequality_check(alpha):  alpha = alpha/2
		return alpha

	def solve(self, sig=0.5, alpha_init=10):
		
		for _ in range(100):
			grad, P = self.gradient_step(self.l_triangle)
		
			alpha = self.step_alpha(sig,alpha_init,self.l_triangle,grad,P)
			#print(alpha)
			self.l_triangle = self.normalize(self.l_triangle+alpha *P)
		return self.l_triangle

