import sys, os

dirname = os.path.abspath(os.path.dirname(__file__))
superdir = os.path.split(dirname)[0]
if not superdir in sys.path:
    sys.path.append(superdir)
    
import turboctl
from turboctl.ui.shell import InteractiveTUI as UI

with turboctl.VirtualPump() as vp:
    ui = UI(vp.port)
    ui.run()