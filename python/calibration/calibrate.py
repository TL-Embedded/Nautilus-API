import os, sys, time
from typing import Callable

sys.path.append(os.path.split(sys.path[0])[0]) # So we can import nautilus
from nautilus import Nautilus
from instrument.TENMA72_132 import TENMA72_132


def check_output(jig: Nautilus, channel: int, setpoint: float = 5.0):
    jig.set_output(channel, True, setpoint)
    time.sleep(0.2)
    v = jig.get_input_voltage(channel)
    print(f"OUT{channel} = {v:.3f}V")
    jig.set_output(channel, False)

def calibrate_psu_voltage(jig: Nautilus, channel: int, eload: TENMA72_132):
    jig.calibrate_psu_voltage(channel, eload.get_voltage)

def check_psu_voltage(jig: Nautilus, channel: int, eload: TENMA72_132, setpoint: float = 5.0 ):
    jig.set_psu(channel, True, setpoint, 0.5)
    time.sleep(1.0)
    v_actual = eload.get_voltage()
    v_meas = jig.get_psu_voltage(channel)
    print(f"PSU{channel} = {v_actual:.3f}V")
    print(f"MEAS{channel} = {v_meas:.3f}V")
    jig.set_psu_enable(channel, False)

def check_psu_current(jig: Nautilus, channel: int, eload: TENMA72_132, setpoint: float = 1.0):
    eload.set_current(2.0)
    eload.set_input(True)

    jig.set_psu(channel, True, 5.0, setpoint)
    time.sleep(1.0)
    i_actual = eload.get_current()
    i_meas = jig.get_psu_current(channel)
    print(f"PSU{channel} = {i_actual:.3f}A")
    print(f"MEAS{channel} = {i_meas:.3f}A")
    jig.set_psu_enable(channel, False)

    eload.set_input(False)

def calibrate_psu_current(jig: Nautilus, channel: int, eload: TENMA72_132):
    eload.set_voltage(2.0)
    eload.set_input(True)
    jig.calibrate_psu_current(channel, eload.get_current)
    eload.set_input(False)

if __name__ == "__main__":

    eload = TENMA72_132()

    with Nautilus() as jig:
        jig.reset()

        for i in range(1, 13):
            check_output(jig, i)
        
        #calibrate_psu_voltage(jig, 2, eload)
        #calibrate_psu_current(jig, 1, eload)
        #jig.calibrate_psu_reset(1)

        #check_psu_voltage(jig, 2, eload)
        #check_psu_current(jig, 1, eload)

    eload.close()
