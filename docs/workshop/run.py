# -*- coding: utf-8 -*-
# Copyright (c) 2025, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

from group import do_move

# This function implements a naive move for enemies, which move down in one turn,
# and up in another, and repeat. Of course, the enemies in the real arena will
# move in every turn to minimise the distance between them and the player...
def naive_enemies_move(enemies, idx):
    if idx % 2 == 0:
        return [(x, y+1) for x, y in enemies]
    else:
        return [(x, y-1) for x, y in enemies]

# An examplar arena
arena = [
    [
        {
            "x": 0,
            "y": 0,
            "type": "free"
        },
        {
            "x": 1,
            "y": 0,
            "type": "free"
        },
        {
            "x": 2,
            "y": 0,
            "type": "mud"
        },
        {
            "x": 3,
            "y": 0,
            "type": "mud"
        },
        {
            "x": 4,
            "y": 0,
            "type": "free"
        }
    ],
    [
        {
            "x": 0,
            "y": 1,
            "type": "free"
        },
        {
            "x": 1,
            "y": 1,
            "type": "mud"
        },
        {
            "x": 2,
            "y": 1,
            "type": "wall"
        },
        {
            "x": 3,
            "y": 1,
            "type": "wall"
        },
        {
            "x": 4,
            "y": 1,
            "type": "free"
        }
    ],
    [
        {
            "x": 0,
            "y": 2,
            "type": "free"
        },
        {
            "x": 1,
            "y": 2,
            "type": "free"
        },
        {
            "x": 2,
            "y": 2,
            "type": "free"
        },
        {
            "x": 3,
            "y": 2,
            "type": "free"
        },
        {
            "x": 4,
            "y": 2,
            "type": "free"
        }
    ],
    [
        {
            "x": 0,
            "y": 3,
            "type": "free"
        },
        {
            "x": 1,
            "y": 3,
            "type": "free"
        },
        {
            "x": 2,
            "y": 3,
            "type": "free"
        },
        {
            "x": 3,
            "y": 3,
            "type": "wall"
        },
        {
            "x": 4,
            "y": 3,
            "type": "wall"
        }
    ],
    [
        {
            "x": 0,
            "y": 4,
            "type": "wall"
        },
        {
            "x": 1,
            "y": 4,
            "type": "mud"
        },
        {
            "x": 2,
            "y": 4,
            "type": "mud"
        },
        {
            "x": 3,
            "y": 4,
            "type": "mud"
        },
        {
            "x": 4,
            "y": 4,
            "type": "mud"
        }
    ]
]

# starting position of the player
start = (2, 2)

# startin position of the enemies
enemies = [(4, 0), (0, 2)]

# the player's diary, with indicated the current position
diary = {
    "position": start
}

# the number of turns
turns = len(arena) * 3

for i in range(turns):
    print("# Turn", i+1, "of", turns)

    # The player moves
    result = do_move(arena, enemies, diary)
    print("\tlist of moves done in this turn:", result)
    
    # Then the enemies move
    enemies = naive_enemies_move(enemies, i)
    print("\tnew enemies positions:", enemies)