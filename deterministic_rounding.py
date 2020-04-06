#imported libs
import numpy as np


""" 

Deterministic rounding of relaxation for MaxCut problem with 2 methods:
- dimensional reduction by Johnson Linderstrauss
- huge dimensional reduction by Ramesh

"""


class Deter_rounding:

	def __init__(self,V):
		#input: V matrix with real numbers, argmax of SDP

		self.V = V
		self.n = V.shape[0]


	def dimensionality_red(self, method='JL'):
		#reduce the dimension of the Vs, and also diminish the size of the set
		if method == 'JL':
			pass

		if method == 'R':
			pass

	def evaluate(self, r):
		return 0

	def generator_max(self):
		# gets the maximum value for generated normal distrib symmetrical vector
		self.dimensionality_red()
		self.evaluate(r)

		return 0
