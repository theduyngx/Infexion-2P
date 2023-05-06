from referee.game import HexPos, HexDir, PlayerColor, \
                         Action, SpawnAction, SpreadAction, \
                         MAX_TOTAL_POWER, BOARD_N

pos1 = HexPos(1, 1)
pos2 = HexPos(1, 1)

dir1 = HexDir.UpRight
dir2 = HexDir.DownLeft

d = {}
d[pos1] = 1
d[pos2] = 1

for e in d.items():
    print(e[0], e[1])

pos3 = pos1 + dir1 * 2
print(pos3)
print(HexDir.UpRight == - HexDir.DownLeft)
print(HexDir.DownRight == - HexDir.UpLeft)
print(HexDir.Down == - HexDir.Up)

for i in range(-1, -(BOARD_N//2+1), -1):
    print(i)

for i in range(1, BOARD_N//2 + 1):
    print(i)
