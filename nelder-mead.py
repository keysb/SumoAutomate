import time
import numpy as np
from scipy.optimize import minimize
from dynamita.sumo import Sumo, dur

t = []
of = []
of_pos = 0

def main():
	global of_pos

	sumo = Sumo(sumoPath="d:/0sw/Sumo20",
        	licenseFile=r"d:/0sw/Sumo20/kcs.sumodyn")
	sumo.register_message_callback(message_callback)
	print(sumo.load_model('NelderMeadTest.sumo'))
	sumo.register_datacomm_callback(datacomm_callback)

	# Get the position of the variable representing the objective function value.
	of_pos = sumo.core.csumo_model_get_variable_info_pos(sumo.handle, b'Sumo__Plant__Objfunc')
	# The starting values for the optimizer (we have only one in this example).
	x0 = np.array([2.0])
	# Call the Nelder-Mead optimizer with the prepared arguments.
	minimize(objfun, x0, sumo, method='nelder-mead', options={'xtol': 1e-2, 'disp': True})

def run_sim(sumo, so2):
	# Start a 10 days simulation with the given parameter.
	sumo.send_command('reset')
	sumo.send_command('set Sumo__Plant__CSTR__param__SO2 ' + '{0}'.format(so2) + ';')
	sumo.set_stopTime(10*dur.day)
	sumo.set_dataComm(dur.hour)

	sumo.run_model()

	# Wait for simulation to be finished.
	while not sumo.simulation_finished:
		time.sleep(0.01)

def datacomm_callback(sumo):
	# Skip inital run with 0 StopTime where variables are not ready yet.
	stop_time = sumo.core.csumo_var_get(sumo.handle, "Sumo__StopTime".encode('utf8'))
	if stop_time == b'0':
		return 0

	# Storing the simulation time and objective function value at this time.
	# This is an example how to do it, not used anywhere.
	t.append(sumo.core.csumo_var_get_time_double(sumo.handle))
	of.append(sumo.core.csumo_var_get_pvt_pos(sumo.handle, of_pos))
	return 0

def message_callback(sumo):
	for message in sumo.messages:
		# Skip chatty Set command reports (remove it if those messages are needed).
		if not message.startswith('530021'):
			print(message)
	sumo.messages = []
	return 0

def objfun(x, sumo):
	print("Trying SO2:", x[-1])
	run_sim(sumo, x[-1])
	of_val = sumo.core.csumo_var_get_pvt_pos(sumo.handle, of_pos)
	print('Objective function value:', of_val)
	return of_val

main()
