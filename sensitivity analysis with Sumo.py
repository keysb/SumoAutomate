from dynamita.sumo import *

import time
import numpy
import matplotlib.pyplot as plt

sumo = Sumo(sumoPath="d:/0sw/Sumo20",
           licenseFile=r"d:/0sw/Sumo20/kcs.sumodyn")

def datacomm_callback(sumo):
    t.append(sumo.core.csumo_var_get_time_double(sumo.handle))
    snhx.append(sumo.core.csumo_var_get_pvtarray_pos(sumo.handle, snhx_pos, 0))
    return 0

def message_callback(sumo):
    for message in sumo.messages:
        print(message)
    sumo.messages = []
    return 0

sumo.register_message_callback(message_callback)

sumo.load_model('cstr.sumo')
sumo.register_datacomm_callback(datacomm_callback)
snhx_pos = sumo.core.csumo_model_get_variable_info_pos(sumo.handle, b'Sumo__Plant__CSTR1__SNHx')
sumo.send_command('set Sumo__Plant__CSTR1__param__XOHO_0 0;')
sumo.send_command('set Sumo__Plant__CSTR1__param__XPAO_0 0;')
sumo.send_command('set Sumo__Plant__CSTR1__param__SNHx_0 5;')

sumo.set_stopTime(2*dur.hour)
sumo.set_dataComm(1*dur.min)

from collections import OrderedDict
snhx_sensitivity_data = OrderedDict()

# So we are going to change the ammonia half-saturation coefficient. 
# For now we just create a list of our desired values manually. 
# If required, Python provides tools to create the required values programmatically - see e.g. the range or linspace methods.
for KNHx in [0.2, 0.4, 0.6, 0.8, 1.0]:
    command = 'set Sumo__Plant__param__Sumo1__KNHx_NITO_AS ' + str(KNHx) + ';'
    sumo.core.csumo_command_send(sumo.handle, command.encode('utf8'))
    
    # Do not forget to empty our lists before a simulation, otherwise
    # new simulation results would just be appended.
    t = []
    snhx = []
    
    # Let's have Sumo do some work
    sumo.run_model()
    # The run_model is an asynchronous call, so we need to wait until
    # the current run is finished, otherwise we would mess up our simulations
    while not sumo.simulation_finished:
        time.sleep(0.01)

    # Good, we got our data in the list, let's store 'em in our dictionary, using 
    # KNHx as the label
    snhx_sensitivity_data[KNHx] = snhx

fig, axes = plt.subplots(1,1)
axes.set_xlabel('time')
axes.set_ylabel('SNHx')

for KNHx, snhx in snhx_sensitivity_data.items():
    axes.plot(t, snhx, label=str(KNHx))
    plt.legend(loc='upper right', title='Legend')
    fig.canvas.draw()

plt.show()
