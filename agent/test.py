"""
    Module  : test.py
    Purpose : For debugging.
"""

from collections import defaultdict

from referee.game import HexPos, HexDir, SpreadAction
from agent.game import Board, CellState, PLAYER_COLOR

pos1  = HexPos(1, 1)
pos2  = HexPos(1, 2)
pos3  = HexPos(4, 2)
pos4  = HexPos(5, 2)
pos5  = HexPos(3, 2)
pos6  = HexPos(0, 6)
pos7  = HexPos(5, 5)
cell1 = CellState(pos1, PLAYER_COLOR, 2)
cell2 = CellState(pos2, PLAYER_COLOR, 1)
cell3 = CellState(pos3, PLAYER_COLOR, 1)
cell4 = CellState(pos4, PLAYER_COLOR, 4)
cell5 = CellState(pos5, PLAYER_COLOR, 3)
cell6 = CellState(pos6, PLAYER_COLOR, 3)
cell7 = CellState(pos7, PLAYER_COLOR, 2)
state = {pos1.__hash__() : cell1, pos2.__hash__() : cell2, pos3.__hash__() : cell3,
         pos4.__hash__() : cell4, pos5.__hash__() : cell5, pos6.__hash__() : cell6,
         pos7.__hash__() : cell7}

eaten = [2, 2, 1, 1, 3, 3, 3]
poses = [pos1 , pos2 , pos3 , pos4 , pos5 , pos6 , pos7 ]
cells = [cell1, cell2, cell3, cell4, cell5, cell6, cell7]
dirs  = [HexDir.UpRight, HexDir.DownRight, HexDir.Down, HexDir.UpLeft, HexDir.Down,
         HexDir.Up, HexDir.DownLeft]
board = Board(state)

actions = []
final: dict[(HexPos, HexDir), int] = defaultdict()
for i in range(7):
    final[(poses[i], dirs[i])] = eaten[i]

action_sorted = sorted(final.items(),
                       key=lambda item: (item[1], board[item[0][0]].power),
                       reverse=True)
(pos, dir), max_capture = action_sorted[0]
max_power = board[pos].power
for (pos, dir), value in action_sorted:
    if value < max_capture or board[pos].power < max_power:
        break
    actions.append(SpreadAction(pos, dir))

# endgame filter works as expected
for action in actions:
    print(action)
