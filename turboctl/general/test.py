import time
from turboctl.virtualpump import VirtualPump

with VirtualPump() as vp:
    hw = vp.hardware_component
    print(hw.frequency)