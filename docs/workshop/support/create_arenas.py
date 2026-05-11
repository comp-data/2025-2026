# -*- coding: utf-8 -*-
# Copyright (c) 2019, Silvio Peroni <essepuntato@gmail.com>
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

from random import shuffle, choice
from networkx import Graph, is_connected
from collections import defaultdict
from argparse import ArgumentParser
from os import makedirs
from os.path import exists, sep
from json import dump

def get_edge_cells(set_of_cells, edge_size):
    result = defaultdict(list)

    for x, y in set_of_cells:
        if 0 <= x < edge_size - 1 and y == 0:
            result["top"].append((x, y))
        elif x == 0 and 1 <= y < edge_size:
            result["left"].append((x, y))
        elif 0 < x < edge_size and y == edge_size - 1:
            result["bottom"].append((x, y))
        elif x == edge_size - 1 and 0 <= y < edge_size - 1:
            result["right"].append((x, y))
    
    return result


def get_number_of_cells(total, p_free, p_wall, p_mud):
    n_free = round((total / 100) * p_free)
    n_wall = round((total / 100) * p_wall)
    n_mud = round((total / 100) * p_mud)

    diff = total - (n_free + n_wall + n_mud)
    while diff != 0:
        if diff > 0:
            val = 1
            diff -= 1
        else:
            val = -1
            diff += 1
        n_free += val
    
    return n_free, n_wall, n_mud

def create_board(edge_size, p_free, p_wall, p_mud):
    free, wall, mud = get_number_of_cells(edge_size * edge_size, p_free, p_wall, p_mud)
    cell_list = free * ["free"] + wall * ["wall"] + mud * ["mud"]
    shuffle(cell_list)

    walking_cells = []
    structure = []
    for y in range(edge_size):
        row = []
        for x in range(edge_size):
            cell = cell_list.pop(0)
            row.append({
                "x": x,
                "y": y,
                "type": cell
            })
            if cell != "wall":
                walking_cells.append((x, y))
        structure.append(row)

    g = Graph()
    for cell in walking_cells:
        g.add_node(cell)
        x, y = cell
        for neig in [(x+1, y), (x-1, y), (x, y-1), (x, y-1)]:
            if neig in walking_cells:
                g.add_edge(cell, neig)
    
    if is_connected(g):
        start = choice(walking_cells)

        enemies = []
        for _ in range(edge_size // 2):
            enemy = None
            while enemy is None:
                enemy = choice(walking_cells)
                if enemy == start or enemy in enemies:
                    enemy = None
                else:
                    enemies.append(enemy)

        return {
            "structure": structure,
            "start": {
                "x": start[0],
                "y": start[1]
            },
            "enemies": [{"x": enemy[0], "y": enemy[1]} for enemy in enemies]
        }
    else:
        return None


if __name__ == "__main__":
    arg_parser = ArgumentParser("Create Board")

    arg_parser.add_argument("-o", "--outdir", required=True,
                            help="The folder where to store the 100 arenas.")
    
    args = arg_parser.parse_args()

    if not exists(args.outdir):
        makedirs(args.outdir)
    
    count_board = 1
    base_edge = 3
    edge_size = base_edge
    multiplier = 0
    divider = 3

    while count_board < 101:
        board = None

        while board is None:
            p_free = 0
            p_mud = 0
            while p_free + p_mud < 75 or p_mud > 30:
                p_free = choice(range(101))
                p_mud = choice(range(101 - p_free))
                p_wall = 100 - (p_free + p_mud)

            board = create_board(edge_size, p_free, p_wall, p_mud)
            if board is not None:
                print(count_board, 
                    f"- Generated arena {edge_size}x{edge_size} with {p_free}% "
                    f"free cells, {p_wall}% walls, and {p_mud}% muds")
        
        with open(args.outdir + sep + str(count_board) + ".json", "w", encoding="utf-8") as f:
            dump(board, f)
        
        multiplier += 1
        edge_size = base_edge * ((multiplier % divider) + 1)
        count_board += 1
