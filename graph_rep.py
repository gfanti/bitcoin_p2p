# graphrep.py

import networkx as nx
import random
from sortedcontainers import SortedDict
import matplotlib.pyplot as plt

# Regular tree that spreads messages according to Bitcoin protocol
class RegularTree(nx.Graph):

	def __init__(self, degree = None, spreading_time = None):
		super(RegularTree, self).__init__()
		self.tree_degree = degree
		self.source = 0
		self.max_node = 1 # highest-index node in the list
		self.active = [0] # list of nodes that are not fully surrounded by infected nodes
		self.spreading_time = spreading_time
		if self.spreading_time is None:
			self.spreading_time = (self.tree_degree * 2 + 1)

		RegularTree.add_node(self,self.source, infected = True)


	def add_node(self, u, attr_dict = None, **attr):
		super(RegularTree, self).add_node(u, attr)
		self.max_node = max(self.nodes())

	def get_neighbors(self, sources):
		neighbors = []
		for source in sources:
			neighbors += self.neighbors(source)
		return list(set(neighbors))

	def subgraph(self, nbunch):
		H = nx.Graph.subgraph(self, nbunch)
		return H

	def add_edges(self, source, node_list):
		for node in node_list:
			self.add_node(node, infected = False)
			self.add_edge(source, node)

	def infect_node(self, source, target):
		if (target == self.adversary):
			self.remove_edge(source, target)
		else:
			self.node[target]['infected'] = True
			self.active += [target]
			

		# Check if the source still has active neighbors; if not, remove it from active list
		uninfected_neighbors = self.get_uninfected_neighbors(source)
		if not uninfected_neighbors:
			self.active.remove(source)

	def get_uninfected_neighbors(self, source):
		neighbors = self.neighbors(source)
		uninfected_neighbors = [neighbor for neighbor in neighbors if self.node[neighbor]['infected'] == False]
		return uninfected_neighbors


class RegularTreeDiffusion(RegularTree):

	def __init__(self, degree = None, spreading_time = None):
		''' NB: Here the spreading_time	is actually the number of rings of the graph to infect'''
		super(RegularTreeGossip, self).__init__(degree, spreading_time)
		self.adversary = -1
		self.lambda1 = 1 # spreading rate over the diffusion graph
		self.lambda2 = 1 # spreading rate from a node to the adversary
		self.adversary_timestamps = {}
		self.received_timestamps = {}

		self.add_node(self.adversary, infected = False)

	def spread_message(self):
		new_boundary = []
		count = 0
		while count < self.spreading_time:
			count += 1
			# cycle through the active nodes, and spread with an exponential clock
			for node in self.active:
				# Check that all the nodes have enough neighbors
				if self.degree(node) < (self.tree_degree):
					num_missing = (self.tree_degree) - self.degree(node)
					new_nodes = range(self.max_node + 1, self.max_node + num_missing + 1)
					self.add_edges(node, new_nodes)
				# Add the new nodes to the boundary
				new_boundary += new_nodes

				# Adversary infection time
				self.adversary_timestamps[node] = self.send_to_adversary(node) 
				# Neighbor infection times
				for new_node in new_nodes:
					self.received_timestamps[new_node] = self.send_to_neighbor(node)

	def send_to_adversary(self, node):
		return self.received_timestamps[node] + np.random.exponential(self.lambda2)

	def send_to_neighbor(self, node):
		return self.received_timestamps[node] + np.random.exponential(self.lambda1)



class RegularTreeGossip(RegularTree):

	def __init__(self, degree = None, spreading_time = None):
		super(RegularTreeGossip, self).__init__(degree, spreading_time)
		self.adversary = -1
		self.adversary_timestamps = SortedDict()

		self.add_node(self.adversary, infected = False)
		

	def add_edge(self, u, v):
		super(RegularTree, self).add_edge(u, v)
		super(RegularTree, self).add_edge(u, self.adversary)
		super(RegularTree, self).add_edge(v, self.adversary)

	def add_node(self, u, attr_dict = None, **attr):
		super(RegularTree, self).add_node(u, attr)
		if not (u == self.adversary):
			super(RegularTree, self).add_edge(u, self.adversary)
		self.max_node = max(self.nodes())

	def generate_timestamp_dict(self):
		''' Creates a dict with nodes as keys and timestamps as values '''
		timestamp_dict = {}
		for key in self.adversary_timestamps.keys():
			for node in self.adversary_timestamps[key]:
				timestamp_dict[node] = key
		return timestamp_dict

	def draw_plot(self):
		values = ['r' for i in self.nodes()]
		values[-1] = 'b'

		pos=nx.circular_layout(self) # positions for all nodes

		nx.draw(self, pos = pos, node_color = values)

		labels={}
		for i in self.nodes():
			labels[i] = str(i)
		nx.draw_networkx_labels(self,pos,labels,font_size=16)

		plt.show()

	def spread_message(self):
		t = 1
		candidates = []
		reached_adversary = False

		
		while (t <= self.spreading_time):
			current_active = [item for item in self.active]
			for node in current_active:
				# Check that all the nodes have enough neighbors
				if ((self.degree(node) < (self.tree_degree + 1) and self.has_edge(node, self.adversary)) or
				   (self.degree(node) < (self.tree_degree) and (not self.has_edge(node, self.adversary)))): 
					if (self.degree(node) < (self.tree_degree + 1) and self.has_edge(node, self.adversary)):
						num_missing = (self.tree_degree + 1) - self.degree(node)
					else:
						num_missing = self.tree_degree - self.degree(node)
					new_nodes = range(self.max_node + 1, self.max_node + num_missing + 1)
					self.add_edges(node, new_nodes)
				
				# print 'adjacency: ', self.edges()

				# Spread to the active nodes' uninfected neighbors
				uninfected_neighbors = self.get_uninfected_neighbors(node)
				# print 'uninfected_neighbors', uninfected_neighbors, 'current_active', current_active, 'node', node
				to_infect = random.choice(uninfected_neighbors)
				self.infect_node(node, to_infect)
				# print 'node ', node, ' infected ', to_infect
				
				
				if to_infect == self.adversary:
					# self.adversary_timestamps.append([node,t])
					if (t in self.adversary_timestamps):
						self.adversary_timestamps[t] += [node]
					else:
						self.adversary_timestamps[t] = [node]
					# self.adversary_timestamps += [t]
					# candidates += [node]
					# reached_adversary = True
			t += 1
		# print 'timestamps:', self.adversary_timestamps

	

