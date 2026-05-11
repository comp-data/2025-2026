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

from networkx import Graph, shortest_path_length
from anytree import Node
from pprint import pprint

def do_move(arena, enemies, diary):
    result = []

    player_pos = diary["position"]

    walking_cells = []
    mud_cells = []
    wall_cells = []
    for row in arena:
        for cell in row:
            if cell["type"] != "wall":
                walking_cells.append((cell["x"], cell["y"]))
            else:
                wall_cells.append((cell["x"], cell["y"])) 
            if cell["type"] == "mud":
                mud_cells.append((cell["x"], cell["y"]))
    
    g = Graph()
    for cell in walking_cells:
        g.add_node(cell)
        x, y = cell
        for neig in [(x+1, y), (x-1, y), (x, y-1), (x, y-1)]:
            if neig in walking_cells:
                g.add_edge(cell, neig)

    root = create_tod(player_pos, enemies, walking_cells, mud_cells, g, 0)

    # Then take those that put the enemies more equally distant
    equally_distance = len(arena) * 2
    best_e_list = []
    for node in (root,) + root.descendants:
        cur_d, indiv_d, cur_p = node.name
        d_e_mean = cur_d / len(indiv_d)
        cur_e_distance = 0
        for d in indiv_d:
            diff = d - d_e_mean
            cur_e_distance += diff if diff >= 0 else -1 * diff
        
        if cur_e_distance < equally_distance:
            best_e_list = [node]
            equally_distance = cur_e_distance
        elif cur_e_distance == equally_distance:
            best_e_list.append(node)

    # Consider only the nodes that have the best distance from enemies
    best_distance = 0
    best_d_list = []
    for node in best_e_list:
        cur_d, indiv_d, cur_p = node.name
        if cur_d > best_distance:
            best_distance = cur_d
            best_d_list = [node]
        elif cur_d == best_distance:
            best_d_list.append(node)
            
    # Then take the one with greater path
    final_node = None
    greater_path = 0
    for node in best_e_list:
        if len(node.ancestors) > greater_path:
            greater_path = len(node.ancestors)
            final_node = node

    if final_node is None:
        final_moves = []
    else:
        final_moves = [node.name[2] for node in list(final_node.ancestors + (final_node,))][1:]
        diary["position"] = final_moves[-1]
    
    return final_moves

def create_tod(cur_pos, enemies_pos, walking_cells, mud_cells, g, level):
    # Identify the distance from the current position
    enemies_distance = []
    for enemy in enemies_pos:
        enemies_distance.append(shortest_path_length(g, enemy, cur_pos))
    cur_node = Node((sum(enemies_distance), enemies_distance, cur_pos))
    
    # If we do not reach the maximum level
    if level < 3:
        children = []

        # Go ahead with the children moves if we are the starting point (level = 0) or
        # the position is not a mud cell (in that case, no moves are allowed)
        if level == 0 or cur_pos not in mud_cells:
            pp_x, pp_y = cur_pos
            for move in [(pp_x+1, pp_y), (pp_x-1, pp_y), (pp_x, pp_y+1), (pp_x, pp_y-1)]:
                # if it is a valid move, proceed recursively to build the tree
                # print(cur_node, move, move in walking_cells)
                if move in walking_cells and move not in enemies_pos:
                    children.append(
                        create_tod(move, enemies_pos, walking_cells, mud_cells, g, level + 1))
        
        if children:
            cur_node.children = children
    
    return cur_node
