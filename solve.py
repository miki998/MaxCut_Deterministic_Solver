from enumerative import *
from graph_reader import *
from greedy import *
from half_approx import *
#from local_search import *
from williamson_approx import *
import numpy as np 
#from lib_solver import *


if __name__ == '__main__':
	X,n,m = graph_read('graph_examples/g05_60.2')
	
	#Enumerative testing
	#enumerate = Enumerative(X,[i for i in range(n)])
	#max_enumerate = enumerate.solve()
	#print('Maximum found by enumerative cutoff method {}'.format(max_enumerate))

	#Greedy testing
	#greedy = Greedy(X,[i for i in range(n)])
	#max_greedy = greedy.solve()
	#print('Maximum found by greedy method {}'.format(max_greedy))	


	#Half_approx testing
	#point_five = Half_rand_algo(X,[i for i in range(n)])
	#max_point_five = point_five.solve()
	#print('Maximum found by half approximative method {}'.format(max_point_five))

	#Williamson random rounding testing
	sdp = Sdp_relax_algo(X,n)
	max_sdp = sdp.solve(method='grad')
	print('Maximum found by williamson method {}'.format(max_sdp))	

	#Standard solving random rounding testing
	sdp = Sdp_relax_algo(X,n)
	max_sdp = sdp.solve()
	print('Maximum found by Standard method {}'.format(max_sdp))

	#Python lib solver
	sol = solve('graph_examples/g05_60.2')
	print(sol)
	print('Maximum found by locallib {}'.format(sol))


	#Optimal value 
	print('Optimal Value happens to be {}'.format(529))



