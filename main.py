# main.py

from graph_rep import *
from estimators import *

degrees = xrange(2,3,2)
trials = 1000
check_ml_flag = False
accuracies_first = []
accuracies_ml_line = []
accuracies_ml = []

for degree in degrees:
	print 'On degree ', degree
	count_first = 0
	count_ml_line = 0
	count_ml = 0

	for i in range(trials):
		if (i % 100) == 0:
			print 'On trial ', i, ' out of ', trials
		G = RegularTree(degree,degree + 1)
		G.spread_message()
		
		# First spy estimator
		est_first = FirstSpyEstimator(G)
		result_first = est_first.estimate_source()
		acc_first = est_first.compute_accuracy(G.source, result_first)
		count_first += acc_first


		# # ML estimator line
		# est_ml_line = MLEstimatorLine(G)
		# result_ml_line = est_ml_line.estimate_source()
		# acc_ml_line = est_ml_line.compute_accuracy(G.source, result_ml_line)
		# count_ml_line += acc_ml_line
		
		if check_ml_flag:
			# ML estimator general
			est_ml = MLEstimatorMP(G)
			result_ml = est_ml.estimate_source()
			acc_ml = est_ml.compute_accuracy(G.source, result_ml)
			count_ml += acc_ml

		# if not acc_ml_line == acc_ml:
		# 	break

	accuracies_first += [float(count_first) / trials]
	accuracies_ml_line += [float(count_ml_line) / trials]
	accuracies_ml += [float(count_ml) / trials]

	print 'accuracies, first-spy:', accuracies_first
	# print 'accuracies, ML line:', accuracies_ml_line
	print 'accuracies, ML:', accuracies_ml

print 'The first-spy estimator accuracy: ', accuracies_first
print 'The ML line estimator accuracy: ', accuracies_ml_line
print 'The ML estimator accuracy: ', accuracies_ml
print 'Tested on degrees', degrees

filename = 'results' + "_".join([str(i) for i in degrees])
f = open(filename, 'w')
val = 'first-spy estimator accuracy: ', accuracies_first
f.write(val)
val = 'ML estimator accuracy: ', accuracies_ml
f.write(val)
val = 'Tested on degrees', degrees
f.write(val)
f.close()