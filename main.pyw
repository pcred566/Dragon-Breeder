"""                           [ ZLIB LICENSE ]
Dragon Breeder -- a game based on breeding dragons
version 1.2.8, April 28th, 2013

Copyright (C) 2016 Stephen Joseph

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
 claim that you wrote the original software. If you use this software
 in a product, an acknowledgment in the product documentation would be
 appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
 misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

Stephen Joseph [pcred566]

                            [ LICENSE EXTENSION ]
All creative assets supplied with the provided software, including images and
music, may be reused or redistributed AS LONG AS the source of said images or
music is clearly labeled AND a link to the source (e.g. the location from which
the files were downloaded) is provided along with the content. If the content
in which the images or music qualifies as 'Fair Use' or 'Derivative' then this
restriction is not applicable and no link to the source is required; however,
if the content is used in an unmodified form or is only slightly modified for
suitable use the origin of the content must be clearly shown."""

# Imports sge, sge.gfx, sge.dsp, and several other modules, along with utility functions.
from gameutils import *

# Create rooms
sge.keyboard.set_repeat(interval=15,delay=450)
sge.game.start_room = MenuRoom()
sge.game.start()
