# utils.py

def write_results(results_names, results_data, param_types, params):
	''' Writes a file containing the parameters, then prints each
	result name with the corresponding data '''

	filename = 'results/results' + "_".join([str(i) for i in params[0]])

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