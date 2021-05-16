from dynamita.sumo import Sumo, dur

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

print("SNHx position is: ", snhx_pos)

sumo.set_stopTime(2*dur.hour)
sumo.set_dataComm(1*dur.min)

t = []
snhx = []

sumo.run_model()

# The run_model is an asynchronous call, so we need to wait until
# the current run is finished, otherwise we would mess up our simulations
while not sumo.simulation_finished:
    time.sleep(0.01)

fig,ax = plt.subplots(1,1)
ax.set_xlabel('time')
ax.set_ylabel('SNHx')
ax.plot(t, snhx)
fig.canvas.draw()

plt.show()


