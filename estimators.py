# estimators.py
import networkx as nx
import random
from sortedcontainers import SortedDict
import itertools
import math
import numpy as np



class Estimator(object):

	def  __init__(self, G, verbose = False):
		self.G = G
		self.verbose = verbose

	def compute_accuracy(self, source, candidates):
		if source in candidates:
			return 1.0 / len(candidates)
		else:
			return 0.0	


class DiffusionEstimator(Estimator):
	def __init__(self, G, verbose = False):
		super(DiffusionEstimator, self).__init__(G, verbose)

class FirstSpyDiffusionEstimator(DiffusionEstimator):

	def __init__(self, G, verbose = False):
		super(FirstSpyDiffusionEstimator, self).__init__(G, verbose)

	def estimate_source(self):
		min_timestamp = float('inf')
		min_node = None
		for node in self.G.nodes():
			if node in self.G.adversary_timestamps:
				if self.G.adversary_timestamps[node] <= min_timestamp:
					min_timestamp = self.G.adversary_timestamps[node]
					min_node = node

		return [min_node]


class GossipEstimator(Estimator):

	def __init__(self, G, verbose = False):
		super(GossipEstimator, self).__init__(G, verbose)

	def get_starting_set(self, timestamp_dict):
		# Gets the set of nodes within an appropriate radius of the 
		# nodes that get the message first

		min_timestamp, candidates_first_spy = self.G.adversary_timestamps.items()[0]
		candidates = set(candidates_first_spy)

		# Then look in an appropriate radius of the first timestamp...
		cand_neighborhood = []
		for candidate in candidates:
			neighborhood = set([candidate])
			for i in range(min_timestamp - 1):
				# print 'neighboring set',set(self.G.get_neighbors(candidates))
				neighborhood = neighborhood.union(set(self.G.get_neighbors(neighborhood)))
			cand_neighborhood += [neighborhood]
		candidates = set.intersection(*cand_neighborhood)
		if self.G.adversary in candidates:
			candidates.remove(self.G.adversary)
		return candidates

class FirstSpyEstimator(GossipEstimator):

	def __init__(self, G, verbose = False):
		super(FirstSpyEstimator, self).__init__(G, verbose)

	def estimate_source(self):
		''' Returns the list of nodes that first delivered the message to 
		the adversary at the same time'''

		min_timestamp, candidates = self.G.adversary_timestamps.items()[0]
		return candidates


class MLEstimator(GossipEstimator):

	def __init__(self, G, verbose = False):
		super(MLEstimator, self).__init__(G, verbose)

	def estimate_source(self):
		''' Returns the list of nodes that have the maximumum likelihood of being
		the true source'''

		# Make sure there are timestamps
		if not any(self.G.adversary_timestamps):
			print 'No timestamps found.'
			return []

		# print 'timestamps are ', self.G.adversary_timestamps
		# print 'adjacency is ', self.G.edges()
		


		# Find the list of eligible nodes, cut 1
		# Start with the first-spy estimate...
		timestamp_dict = self.G.generate_timestamp_dict()
		candidates = self.get_starting_set(timestamp_dict)

		# print 'candidates are', candidates, 'before pruning'
		# print 'timestamp_dict', timestamp_dict
		# self.G.draw_plot()
		# Now check if each of these nodes in the radius is eligible

		final_candidates = [i for i in candidates]
		for candidate in candidates:
			# print 'candidate', candidate
			valid = True
			# print 'candidate', candidate, ' has timestamp', timestamp_dict[candidate]
			for node in candidates:
				timestamp = timestamp_dict[node]
				# print 'node', node
				# print 'timestamp',timestamp, 'lb', self.min_timestamp(candidate, node), 'ub', self.max_timestamp(candidate, node)
				if not self.check_node(candidate, node, timestamp):
					valid = False
					# print 'FAIL candidate', candidate
					break
			if not valid:
				final_candidates.remove(candidate)

		# print 'ml candidates are', final_candidates
		return final_candidates


	def check_node(self, source, target, timestamp):
		''' Checks if target's timestamp is eligible'''
		lowerbound = (timestamp >= self.min_timestamp(source, target))
		upperbound = (timestamp <= self.max_timestamp(source, target))
		return (lowerbound and upperbound)

	def min_timestamp(self, source, target):
		return (nx.shortest_path_length(self.G, source = source, target = target) + 1)

	def max_timestamp(self, source, target):
		d = self.G.tree_degree
		pathlength = nx.shortest_path_length(self.G, source = source, target = target)

		if pathlength == 0:
			return (d + 1)
		return (d + 1) + (d * pathlength)


class MLEstimatorMP(GossipEstimator):

	def __init__(self, G, verbose = False):
		super(MLEstimatorMP, self).__init__(G, verbose)
		self.timestamp_dict = None
		self.rx_time = {}
		self.count_dict = {}
		self.adversary = self.G.adversary
		

	def estimate_source(self):
		''' Returns the list of nodes that have the maximumum likelihood of being
		the true source'''

		# Make sure there are timestamps
		if not any(self.G.adversary_timestamps):
			print 'No timestamps found.'
			return []


		# Get the starting set of nodes
		self.timestamp_dict = self.G.generate_timestamp_dict()
		# try not updating boundary nodes
		# ---------------------------------self.update_boundary_nodes()
		candidates = self.get_starting_set(self.timestamp_dict)

		if self.verbose:
			# print 'timestamps are ', self.G.adversary_timestamps
			print 'adjacency is ', self.G.edges()
			print 'candidates are', candidates
			print 'timestamps are: ', self.timestamp_dict
		# self.G.draw_plot()
		# Now check if each of these nodes in the radius is eligible

		# Now compute the number of paths of viable infection for each node
		final_candidates = [i for i in candidates]

		# Modify the graph to include "boundary nodes"

		counts = []

		# print 'adjacency', self.G.edges()


		# print 'candidates: ', candidates, 'timestamps', self.timestamp_dict, '\n'
		for candidate in candidates:
			if self.verbose:
				print '\nprocessing candidate ', candidate, '\n'

			self.feasible = True
			# -----Run the message-passing------
			count = self.pass_down_messages(candidate, candidate)
			
			if self.verbose:
				print 'candidate', candidate, ' has count ', count
			
			counts += [count]

		if self.verbose:
			print 'candidates counts are ', zip(candidates, counts)

		final_candidates = [candidate for (candidate, score) in zip(candidates, counts) if score == max(counts)]
		return final_candidates


	def update_boundary_nodes(self):
		''' Make it look like all the nodes at the boundary have timestamp T+1 '''
		for n in self.G.nodes():
			# if self.G.node[n]['infected'] and (n not in self.timestamp_dict):
			# 	self.timestamp_dict[n] = self.G.spreading_time + 1
			if (not n == self.G.adversary) and (n not in self.timestamp_dict):
				self.timestamp_dict[n] = self.G.spreading_time + 1

	def get_tree_neighbors(self, node, remove_item = None):
		''' Get a node's neighbors that are infected and not the adversary, except 
		    for item remove_item'''

		neighbors = [n for n in self.G.neighbors(node) if 
						(self.G.node[n]['infected'] == True) and
						not (n == self.adversary) and
						not (n == remove_item) and 
						(n in self.timestamp_dict)]
		return neighbors
			
	def compute_tx_time(self, target, source_flag = False):
		# Otherwise, create the list of possible rx times for the children of target
		tx_time = set()

		if self.verbose:
			print 'self.rx_time[', target, '] = ', self.rx_time[target]
		for t in self.rx_time[target]:
			if source_flag:
				tx_time.update([t+i for i in range(1, self.G.tree_degree + 2)])
			else:
				tx_time.update([t+i for i in range(1, self.G.tree_degree + 1)])
		tx_time = list(tx_time)
		try:
			tx_time.remove(self.timestamp_dict[target])
		except:
			pass
		return tx_time

	def pass_down_messages(self, source, target):
		''' Pass messages down the tree with the feasible set of timestamps'''

		# If source = target, then we're at the root
		if source == target:
			self.rx_time[source] = [0]
			if self.verbose:
				print 'self.rx_time[', source, '] = ', self.rx_time[source]

			# Get the child nodes
			child_nodes = self.get_tree_neighbors(target)

		else:
			# Make sure that there's an edge between source and target
			if not self.G.has_edge(source, target):
				return 0		

			# Identify the target's child nodes
			child_nodes = self.get_tree_neighbors(target, source)

		# Initialize the down messages		
		self.count_dict[target] = {}
		for rx_time in self.rx_time[target]:
			self.count_dict[target][rx_time] = 0
		# print 'dict for target ', target, 'looks like dis', self.count_dict[target]

		# If we're at a leaf, stop passing the message
		if not child_nodes:
			# Now set the up-messages to unit value
			for item in self.rx_time[target]:
				self.count_dict[target][item] = 1 # number of permutations possible (i.e. 1)
			# print 'at a leaf', target
			return

		# Otherwise, create the list of possible rx times for the children of target
		tx_time_baseline = self.compute_tx_time(target, source == target)
		# print 'at first, tx_time was ', tx_time_baseline

		tx_time_list = []
		# Pass the message to child nodes
		for child in child_nodes:
			# Remove any nonphysical timestamps in the rx_time, 
			# i.e. rx_times that happen after the  target's observed timestamp
			
			tx_time = [i for i in tx_time_baseline]

			# Prune the possible tx_times based on the observed timestamps at the receiver
			# print 'child ', child, 'has timestamp', self.timestamp_dict[child], 'and our spreading_time is ', self.G.spreading_time
			# if (self.timestamp_dict[child] > self.G.tree_degree):
			# 	tx_time = [i for i in tx_time if (i >= self.timestamp_dict[child] - self.G.tree_degree)]
			# else:
			tx_time = [i for i in tx_time if (i >= self.timestamp_dict[child] - self.G.tree_degree)
					   					 and (i < self.timestamp_dict[child])]
			# print 'pruned tx_time for child', child, ' is:',tx_time

			self.rx_time[child] = tx_time
			if self.verbose:
				print 'self.rx_time[', child, '] = ', tx_time
			
			# If there are no valid timestamps, then this candidate is not feasible
			if not tx_time:
				return

			# Add the node's feasible rx_times to the list
			tx_time_list += [tx_time]
			self.pass_down_messages(target, child)



		# Aggregate the messages from the children and pass it up the chain
		# order of tx_time_list is [child_nodes target]
		self.aggregate_messages(target, child_nodes, tx_time_list)
		# print 'after dict for target ', target, 'is ', self.count_dict[target]
			
		# print 'degree', self.G.tree_degree

		# if we're at the root, sum up all the elements in the dictionary
		if (source == target):
			# print 'counts from neighbors', self.count_dict[source].keys(), self.count_dict[source].values()
			return sum(self.count_dict[source].values())
		

	def aggregate_messages(self, node, neighbors, tx_time_list):
		# Aggregate the messages from the children and pass it up the chain
		# order of tx_time_list is [child_nodes target]
		# print 'target', node, 'child_nodes', neighbors, 'tx_time_list', tx_time_list
		coordinates = neighbors + [node]
		tx_time_list += [self.rx_time[node]]
		# print 'tx_time_list', tx_time_list
		tuple_list = [list(item) for item in list(itertools.product(*tx_time_list)) if len(set(item)) == len(item)]
		tuple_list = [item for item in tuple_list if ((max(item) - min(item)) <= (self.G.tree_degree+1)) ]
		
		# print 'tuple_list', tuple_list


		# Count the number of paths that use each candidate arrival time at the source
		for item in tuple_list:
			# Multiply the counts associated with each coordinate
			m = [self.count_dict[neighbors[i]][item[i]] for i in range(len(item)-1)]
			self.count_dict[node][item[-1]] += np.prod(m)
			# print 'm is ', m

			# Sum the logs of the counts
			# m = [math.log(self.count_dict[neighbors[i]][item[i]]) for i in range(len(item)-1)]
			# # Instead of multiplying the values, we add the sum
			# self.count_dict[node][item[-1]] += sum(m)

		if self.verbose:
			print 'up-counts for ', node, 'is ', self.count_dict[node]
			





