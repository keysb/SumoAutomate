from dynamita.sumon import Sumo, dur
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


t = []
snhx = []
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

sumo.set_stopTime(2*dur.hour)
sumo.set_dataComm(1*dur.min)

sumo.run_model()

# The run_model is an asynchronous call, so we need to wait until
# the current run is finished, otherwise we would mess up our simulations
while not sumo.simulation_finished:
    time.sleep(0.01)

sumo.unload_model()
sumo.destroy()

print("Data length:", len(snhx))

fig,ax = plt.subplots(1,1)
ax.set_xlabel('time')
ax.set_ylabel('SNHx')
ax.plot(t, snhx)
fig.canvas.draw()

plt.show()
