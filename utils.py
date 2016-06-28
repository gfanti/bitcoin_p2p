# utils.py
import argparse

def write_results(results_names, results_data, param_types, params, run_num = None):
	''' Writes a file containing the parameters, then prints each
	result name with the corresponding data '''

	filename = 'results/results' + "_".join([str(i) for i in params[0]])

	if not (run_num is None):
		filename += '_run' + str(run_num)


	f = open(filename, 'w')

	for (param_type, param) in zip(param_types, params):
		f.write(param_type)
		f.write(': ')
		for item in param:
		  f.write("%s " % item)		
		f.write('\n')

	for (result_type, result) in zip(results_names, results_data):
		f.write(result_type)
		f.write('\n')

		for item in result:
		  f.write("%s " % item)
	  	f.write('\n')

	f.close()

def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", "--run", type=int,
	                    help="changes the filename of saved data")
	parser.add_argument("-v", "--verbose", help="increase output verbosity",
	                    action="store_true")
	parser.add_argument("-w", "--write", help="writes the results to file",
	                    action="store_true")
	parser.add_argument("-t","--trials", type=int, help="number of trials",
						default=1)
	parser.add_argument("--measure_time", help="measure runtime?",
						action="store_true")
	args = parser.parse_args()

	if not (args.run is None):
		args.write = True

	print '---Selected Parameters---'
	print 'verbose: ', args.verbose
	print 'write to file: ', args.write
	print 'run: ', args.run
	print 'num trials: ', args.trials, '\n'
	return args
