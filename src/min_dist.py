import sys
sys.path.append('src/')
from boards import boards
from collections import deque


def create_min_dist():
    board = boards[0]
    ans = {}
    for i in range(len(board)):
        for j in range(len(board[0])):
            used = set()
            if board[i][j] not in [0, 1, 2, 9]:
                continue
            q = deque()
            q.append((i, j, 0))
            used.add((i, j))
            ans[(i, j), (i, j)] = 0
            while q:
                v = q.popleft()
                possible_vertices = [(v[0] - 1, v[1]), (v[0] + 1, v[1]),
                                     (v[0], v[1] - 1), (v[0], v[1] + 1)]
                if v == (15, 0):
                    possible_vertices.append((15, len(board[0]) - 1))
                if v == (15, len(board[0]) - 1):
                    possible_vertices.append((15, 0))
                for u in possible_vertices:
                    if (0 <= u[0] < len(board)) and (
                            0 <= u[1] < len(board[0])) and (
                            board[u[0]][u[1]] in [0, 1, 2, 9]) and (
                            u not in used):
                        used.add(u)
                        ans[((i, j), u)] = v[2] + 1
                        q.append((u[0], u[1], v[2] + 1))
    return ans


min_dist = create_min_dist()
