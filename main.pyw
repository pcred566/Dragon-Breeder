# Imports sge, sge.gfx, sge.dsp, and random modules, along with utility functions.
from gameutils import *

# Create rooms
sge.game.start_room = MenuRoom(background=background)
sge.game.start()
