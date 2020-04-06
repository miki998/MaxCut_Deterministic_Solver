import localsolver
import sys

def read_integers(filename):
	with open(filename) as f:
		return [int(elem) for elem in f.read().split()]


def solve(filename):
	with localsolver.LocalSolver() as ls:

		#
		# Reads instance data
		#

		file_it = iter(read_integers(filename))
		# Number of vertices
		n = next(file_it)
		# Number of edges
		m = next(file_it)

		# Origin of each edge
		origin = [None]*m
		# Destination of each edge
		dest = [None]*m
		# Weight of each edge
		w = [None]*m

		for e in range(m):
			origin[e] = next(file_it)
			dest[e] = next(file_it)
			w[e] = next(file_it)


		model = ls.model

		# Decision variables x[i]
		# Is true if vertex x[i] is on the right side of the cut and false if it is on the left side of the cut
		x = [model.bool() for i in range(n)]

		# incut[e] is true if its endpoints are in different class of the partition
		incut = [None]*m
		for e in range(m):
			incut[e] = model.neq(x[origin[e] - 1], x[dest[e] - 1])

		# Size of the cut
		cut_weight = model.sum(w[e]*incut[e] for e in range(m))
		model.maximize(cut_weight)

		model.close()

		#
		# Param
		#
		if len(sys.argv) >= 4: ls.param.time_limit = int(sys.argv[3])
		else: ls.param.time_limit = 10

		ls.solve()
		return ls