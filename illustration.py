#Imported libs
from graph_tool.all import *


class Graphi:

	#in our case we consider unweighted undirected graphs
	def __init__(self, N, edges):
		#edges: adjency matrix
		#N: number of vertex
		self.N = N
		self.edges = edges
		self.g = Graph(directed=False)

		#initialization
		vertices = [self.g.add_vertex() for _ in range(N)]
		for i in range(N):
			for j in range(i+1,N):
				if self.edges[i][j]: self.g.add_edge(vertices[i],vertices[j])

	def verify(self):
		assert self.edges.shape[0] == self.N
		assert sum(self.edges == 0 or self.edges == 1) == self.N**2

	def illustrate_generator(self):
		graph_draw(g, vertex_text=g.vertex_index, vertex_font_size=18,
	            output_size=(500, 500), output="graph.png")


