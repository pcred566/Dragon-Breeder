# Imports sge, sge.gfx, sge.dsp, and several other modules, along with utility functions.
from gameutils import *

# Create rooms
sge.keyboard.set_repeat(interval=15,delay=450)
sge.game.start_room = MenuRoom()
sge.game.start()