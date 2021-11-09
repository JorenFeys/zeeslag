from random import randint, shuffle


class Battleship:

    def __init__(self, grid_dim, boat_length, bombs):

        self.grid_dim = grid_dim
        self.boat_length = boat_length
        self.bombs = bombs
        self.bombs_left = bombs
        self.hit = False
        self.sunk = False

        self._grid = None
        self.__boat = None
        self.__create_grid()
        self.__position_boat()

    def __create_grid(self):
        # initialize grid with zeros
        n = self.grid_dim
        self._grid = [[0 for column in range(n)] for row in range(n)]

    def __position_boat(self):

        # initialize
        n = self.grid_dim
        self.__boat = [[False for column in range(n)] for row in range(n)]

        # first cell
        n -= 1
        row = randint(0, n)
        column = randint(0, n)
        self.__boat[row][column] = True

        # shuffle directions
        directions = [0, 1, 2, 3]  # 0=N, 1=O, 2=Z, 3=W
        shuffle(directions)

        # others cells
        j = self.boat_length - 1
        for d in directions:
            if (d == 0) and ((row - j) >= 0):
                for i in range(row - j, row):
                    self.__boat[i][column] = True
                break
            elif (d == 1) and ((column + j) <= n):
                for i in range(column + 1, column + j + 1):
                    self.__boat[row][i] = True
                break
            elif (d == 2) and ((row + j) <= n):
                for i in range(row + 1, row + j + 1):
                    self.__boat[i][column] = True
                break
            elif (d == 1) and ((column - j) >= 0):
                for i in range(column - j, column):
                    self.__boat[row][i] = True
                break

    def drop_bomb(self, row, column):
        self.bombs_left -= 1
        try:  # assume input is correct
            self.hit = self.__boat[row][column]
            self._grid[row][column] = 1 if self.hit else -1
        except:  # wrong input -> miss
            self.hit = False
        if self.hit:
            hits = sum([column for row in self._grid for column in row if column == 1])
            self.sunk = hits == self.boat_length
