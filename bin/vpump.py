#!/usr/bin/env python3

import os
import sys

# Add the path to turboctl:
dirname = os.path.abspath(os.path.dirname(__file__))
superdir = os.path.split(dirname)[0]
if not superdir in sys.path:
    sys.path.append(superdir)
    
from turboctl import VirtualPump

vp = VirtualPump()
print(vp.port)
input()
vp.close()