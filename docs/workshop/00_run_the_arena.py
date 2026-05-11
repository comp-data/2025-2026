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

import traceback
import signal
from json import load
from os.path import exists, sep
from networkx import Graph, shortest_path_length
from os import remove
from collections import Counter
from math import sqrt
import mok

RIGHT = "right"
LEFT = "left"
UP = "up"
DOWN = "down"


def load_room(room_file_path):
    with open(room_file_path, encoding="utf-8") as f:
        room_json = load(f)
        
        return (
            room_json["structure"], 
            (room_json["start"]["x"], room_json["start"]["y"]), 
            [(enemy["x"], enemy["y"]) for enemy in room_json["enemies"]])


def is_valid_move(init_position, moves, walls, muds, limit):
    x, y = init_position
    previous_mud = False

    # If all moves are maximum three...
    if len(moves) <= 3:
        for move in moves:
            # ... and if the move is not subsequent to a mud cell...
            if not previous_mud:
                # ... and the move is within the board...
                if x > -1 and x < limit and y > -1 and y < limit:
                    # ... and it is not conflicting with any of the walls ...
                    if (x, y) not in walls:
                        # ... and it is an adjacent move to the current position
                        if move in {(x, y+1), (x, y-1), (x+1, y), (x-1, y)}:
                            x, y = move
                            previous_mud = move in muds
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
    else:
        return False

    return True


def get_walls(room):
    walls = set()

    for row in room:
        for cell in row:
            if cell["type"] == "wall":
                walls.add((cell["x"], cell["y"]))
    
    return walls


def get_muds(room):
    walls = set()

    for row in room:
        for cell in row:
            if cell["type"] == "mud":
                walls.add((cell["x"], cell["y"]))
    
    return walls


def move_enemies(enemies, player_pos, walls, limit, arena):
    walking_cells = []
    for row in arena:
        for cell in row:
            if cell["type"] != "wall":
                walking_cells.append((cell["x"], cell["y"]))
    
    g = Graph()
    for cell in walking_cells:
        g.add_node(cell)
        x, y = cell
        for neig in [(x+1, y), (x-1, y), (x, y-1), (x, y-1)]:
            if neig in walking_cells:
                g.add_edge(cell, neig)

    result = list(enemies)
    for e_x, e_y in enemies:
        cur_d = shortest_path_length(g, (e_x, e_y), player_pos)
        for x, y in {(e_x, e_y+1), (e_x, e_y-1), (e_x+1, e_y), (e_x-1, e_y)}:
            # The move is within the board...
            if x > -1 and x < limit and y > -1 and y < limit:
                # ... and it is not conflicting with any of the walls ...
                if (x, y) not in walls:
                    # ... and it is not currently occupied by another enemy ...
                    if (x, y) not in result:
                        new_d = shortest_path_length(g, (x, y), player_pos)
                        # ... and the move puts the enemy closer to the player
                        if new_d < cur_d:
                            result.remove((e_x, e_y))
                            result.append((x, y))
                            break

    return result


def handle_timeout(signum, frame):
    raise TimeoutError


def play(players, start_pos, room, enemies, turns):
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(5)

    cheaters, loosers, winners = set(), set(), set()
    walls = get_walls(room)
    muds = get_muds(room)
    cur_pos = {}

    for player in players:
        player_name = player.__name__
        winners.add(player_name)
        cur_pos[player_name] = {
            "position": start_pos,
            "diary": {
                "position": start_pos
            },
            "enemies": list(enemies)
        }

    for i in range(turns):
        print("\tTurn", i+1, "of", turns)
        for player in players:
            player_name = player.__name__
            if player_name in winners:
                try:
                    player_moves = player.do_move(
                        room,
                        cur_pos[player_name]["enemies"],
                        cur_pos[player_name]["diary"])

                    is_valid = is_valid_move(
                        cur_pos[player_name]["position"], player_moves, 
                        walls, muds, len(room[0]))
                    
                    # if the moves done by the player are valid, then continue the turn
                    if is_valid:
                        # in case any of the moves clashes on an enemy the player dies
                        if any([move in enemies for move in player_moves]):
                            print("\t\t", player_name, "died")
                            loosers.add(player_name)
                            winners.remove(player_name)
                        else:
                            # if a move is done, the new position is set as the last one
                            if player_moves:
                                cur_pos[player_name]["position"] = player_moves[-1]

                            # the enemies move
                            new_enemies_pos = move_enemies(
                                cur_pos[player_name]["enemies"], 
                                cur_pos[player_name]["position"], 
                                walls, len(room[0]), room)
                            
                            # if any of the enemies clashes with the player, the player dies
                            if cur_pos[player_name]["position"] in new_enemies_pos:
                                print("\t\t", player_name, "died")
                                loosers.add(player_name)
                                winners.remove(player_name)
                            # otherwise, the new enemies position are recorded
                            else:
                                cur_pos[player_name]["enemies"] = new_enemies_pos
                    else:
                        print("\t\t", player_name, "cheated")
                        cheaters.add(player_name)
                        winners.remove(player_name)
                except TimeoutError as e:
                    print("\t\t", player_name, "too long to take decision", traceback.format_exc())
                    cheaters.add(player_name)
                    winners.remove(player_name)
                except Exception as e:
                    print("\t\t", player_name, "cheated", traceback.format_exc())
                    cheaters.add(player_name)
                    winners.remove(player_name)

    return cheaters, loosers, winners


if __name__ == "__main__":
    all_players = [mok]

    final_results = {
        "cheaters": {},
        "winners": {},
        "loosers": {},
    }

    if exists("00_results.txt"):
        remove("00_results.txt")

    all_players_name = set()
    for player in all_players:
        player_name = player.__name__
        all_players_name.add(player_name)
        final_results["cheaters"][player_name] = 0
        final_results["winners"][player_name] = 0
        final_results["loosers"][player_name] = 0

    for idx in range(1, 101):
        print("# Arena", idx)

        room, start, enemies = load_room("arenas" + sep + str(idx) + ".json")
        edge_size = len(room)
        
        cheaters, loosers, winners = play(all_players, start, room, enemies, edge_size * 3)

        for player_name in cheaters:
            final_results["cheaters"][player_name] += 1

        for player_name in loosers:
            final_results["loosers"][player_name] += 1
        
        for player_name in winners:
            final_results["winners"][player_name] += 1

        winners_string = ", ".join(sorted([player for player in winners]))
        loosers_string = ", ".join(sorted([player for player in loosers]))
        cheaters_string = ", ".join(sorted([player for player in cheaters]))
        
        with open("00_results.txt", "a", encoding="utf-8") as f:
            f.write("\n" + "# Room " + str(idx) + "\n\twinners: "+ winners_string + "\n\tloosers: "+ loosers_string + "\n\tcheaters: "+ cheaters_string + "\n")
    
    # 1. Avoiding cheating
    avoid_cheating = all_players_name.difference(set(
        [player_name for player_name in final_results["cheaters"] 
         if final_results["cheaters"][player_name] > 0]))

    # 2. Winning at least 30 rooms
    win_30 = set([player_name for player_name in final_results["winners"] 
                      if final_results["winners"][player_name] > 29])

    # 3. Winning at least 90 rooms
    win_90 = set([player_name for player_name in final_results["winners"] 
                      if final_results["winners"][player_name] > 89])

    final_results_str = "\n\n## FINAL RESULTS ##\nAvoiding cheating: " +  " ".join(avoid_cheating) + "\nWinning at least 30 arenas: " + " ".join(win_30) + "\nWinning at least 90 arenas: " + " ".join(win_90)

    with open("00_results.txt", "a", encoding="utf-8") as f:
        f.write(final_results_str)
    
    print(final_results_str)
