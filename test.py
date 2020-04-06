import numpy as np


def distance(m,n):
	bol = abs(m-n)>10**(-9)
	if not bol: print(m,n)
	return bol



if __name__ == '__main__':
	np.random.seed(10)
	init = np.random.normal()
	count = 0
	while distance(init,np.random.normal()): count += 1
	print(count)
