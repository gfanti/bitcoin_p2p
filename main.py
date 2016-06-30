# main.py

from graph_rep import *
from estimators import *
from utils import *
import time

if __name__ == "__main__":
	
	
	degrees = xrange(2,4,1)
	check_ml = True


	args = parse_arguments()

	accuracies_first = []
	accuracies_ml_line = []
	accuracies_ml = []

	if args.measure_time:
		start = time.time()
		end = start
	for degree in degrees:
		print 'On degree ', degree
		count_first = 0
		count_ml_line = 0
		count_ml = 0

		for i in range(args.trials):
			if (i % 100) == 0:
				print 'On trial ', i+1, ' out of ', args.trials

			# Gossip trials
			G = RegularTreeGossip(degree,degree+3)
			G.spread_message()
			
			# First spy estimator
			est_first = FirstSpyEstimator(G)
			result_first = est_first.estimate_source()
			acc_first = est_first.compute_accuracy(G.source, result_first)
			count_first += acc_first

			if check_ml:
				# ML estimator general
				est_ml = MLEstimatorMP(G, args.verbose)
				result_ml = est_ml.estimate_source()
				acc_ml = est_ml.compute_accuracy(G.source, result_ml)
				count_ml += acc_ml


			# Diffusion trials
			G = RegularTreeGossip(degree,4)
			G.spread_message()


		accuracies_first += [float(count_first) / args.trials]
		accuracies_ml_line += [float(count_ml_line) / args.trials]
		accuracies_ml += [float(count_ml) / args.trials]

		print 'accuracies, first-spy:', accuracies_first
		# print 'accuracies, ML line:', accuracies_ml_line
		print 'accuracies, ML:', accuracies_ml

		if args.write:
			result_types = ['first-spy accuracy', 'ML accuracy']
			param_types = ['degrees']
			results = [[accuracies_first], [accuracies_ml]]
			params = [[i for i in degrees]]
			write_results(result_types, results, param_types, params, args.run)

	print 'The first-spy estimator accuracy: ', accuracies_first
	print 'The ML estimator accuracy: ', accuracies_ml
	print 'Tested on degrees', degrees

	if args.measure_time:
		end = time.time()
		print 'The runtime is ', end-start
