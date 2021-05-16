from dynamita.sumon import Sumo, dur
from collections import OrderedDict
import time
import matplotlib.pyplot as plt

def datacomm_callback(sumo):
    t.append(sumo.time_days())
    snhx.append(sumo.SV(b'Sumo__Plant__CSTR1__SNHx'))
    print(sumo.time_ms(), "ms\t", t[-1], "day(s)\tSNHx:", snhx[-1])
    return 0


def message_callback(sumo):
    for message in sumo.messages:
        print(message)
    sumo.messages = []
    return 0


sumo = Sumo(
    sumoPath="d:/0sw/Sumo20",
    licenseFile="d:/0sw/Sumo20/kcs.sumodyn"
)

sumo.add_message_callback(message_callback)
sumo.add_datacomm_callback(datacomm_callback)

print("Load model:", sumo.load_model("cstr.sumo"))

sumo.send_command('set Sumo__Plant__CSTR1__param__XOHO_0 0;')
sumo.send_command('set Sumo__Plant__CSTR1__param__XPAO_0 0;')
sumo.send_command('set Sumo__Plant__CSTR1__param__SNHx_0 5;')

#sumo.send_command('mode steady')
sumo.set_stopTime(2*dur.hour)
sumo.set_dataComm(1*dur.min)

snhx_sensitivity_data = OrderedDict()

# We are going to change the ammonia half-saturation coefficient. 
# For now we just create a list of our desired values manually. 
# If required, Python provides tools to create the required values programmatically - see e.g. the range or linspace methods.
for KNHx in [0.2, 0.4, 0.6, 0.8, 1.0]:
    command = 'set Sumo__Plant__param__Sumo1__KNHx_NITO_AS ' + str(KNHx) + ';'
    sumo.send_command(command)

    # Do not forget to empty our lists before a simulation, otherwise
    # new simulation results would just be appended.
    t = []
    snhx = []

    sumo.run_model()    
    # The run_model is an asynchronous call, so we need to wait until
    # the current run is finished, otherwise we would mess up our simulations
    while not sumo.simulation_finished:
        time.sleep(0.01)

    # The dictionary stores the data list at every iteration
    # labeling it with KNHx.
    snhx_sensitivity_data[KNHx] = snhx
    print("Simulation end, t:", len(t), "snhx:", len(snhx))


sumo.unload_model()
sumo.destroy()

for KNHx, snhx in snhx_sensitivity_data.items():
    print("KNHx:", KNHx, "list size:", len(snhx))

fig, axes = plt.subplots(1,1)
axes.set_xlabel('time')
axes.set_ylabel('SNHx')

for KNHx, snhx in snhx_sensitivity_data.items():
    axes.plot(t, snhx, label=str(KNHx))
    plt.legend(loc='upper right', title='Legend')
    fig.canvas.draw()

plt.show()
