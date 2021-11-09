from IPython.display import clear_output
from flask_ngrok import run_with_ngrok
from flask import Flask, request
from abc import ABC, abstractmethod
from battleship.game import Battleship


class UserInterface(Battleship, ABC):

    def __init__(self, grid_dim, boat_length, bombs):
        super().__init__(grid_dim, boat_length, bombs)

    @abstractmethod
    def play(self):
        pass


class CommandLineInterface(UserInterface):

    def __init__(self, grid_dim, boat_length, bombs):
        super().__init__(grid_dim, boat_length, bombs)
        self._newline = '\n'
        self._spaces = "  "

    def _grid_to_string(self):

        # grid and its dimension
        grid = self._grid
        n = self.grid_dim

        # column numbers
        numbers = [str(i) for i in range(n)]
        grid_string = [self._spaces + " ".join(numbers)]

        # rows
        for i in range(n):
            row = ["." if column == 0 else "x" if column == 1 else "o" for column in grid[i]]
            grid_string.append(numbers[i] + " " + " ".join(row))
        grid_string = self._newline.join(grid_string) + self._newline

        # output grid string
        return grid_string

    def _message(self):

        # string indicating the number of bombs that are left
        bombs_left = self.bombs_left
        bomb_string = f"{bombs_left} bomb" + ("s" if bombs_left > 1 else "")

        # no bombs dropped yet: start of the game
        if bombs_left == self.bombs:
            msg = f"You have {bomb_string} to destroy the submarine. Good hunting!"

        # boot is gezonken:
        elif self.sunk:
            msg = "Congrats!! The submarine has been destroyed!"

        # all bombs are dropped and the boat has not sunk
        elif bombs_left == 0:
            msg = "No more bombs and the submarine is still cruising..."

        # bombs left and the boat is still cruising
        else:
            msg = ("Hit!!" if self.hit else "Miss!") + f" You have {bomb_string} left..."

        # add newline
        msg = self._newline + msg

        # output string
        return msg

    def _game_display(self):
        return self._grid_to_string() + self._message()

    def play(self):

        # print display
        print(self._game_display())

        # ask for input while bombs left and boat has not sunk
        while self.bombs_left > 0 and not self.sunk:
            # player's input: row and column
            row = int(input("Rij: "))
            column = int(input("Column: "))

            # drop bomb
            self.drop_bomb(row, column)

            # clear previous display and print new one
            clear_output(wait=True)
            print(self._game_display())


class WebInterface(CommandLineInterface):

    def __init__(self, grid_dim, boat_length, bombs):
        super().__init__(grid_dim, boat_length, bombs)
        self._newline = '<br>'
        self._spaces = '&nbsp;' * 2

    def _grid_to_string(self):
        grid_string = super()._grid_to_string()
        grid_string = f'<p style="font-family:\'Courier New\'; font-weight: bold; font-size:30px">{grid_string}</p>'
        return grid_string

    def _message(self):
        msg = super()._message()
        msg = f'<p>{msg}</p>'
        return msg

    @staticmethod
    def __html_form():
        # HTML form
        return """
        <form method="post">
        <label for="row">Row:</label>
        <input type="text" name="row" autofocus><br><br>
        <label for="column">Column:</label>
        <input type="text" name="column"><br><br>
        <button type="submit">Submit</button>
        </form>
        """

    def play(self):

        # create WSGI server app
        app = Flask(__name__)
        run_with_ngrok(app)

        # function that creates HTML for client browser
        # as response to HTTP requests GET en POST
        #   GET: start of the game
        #   POST: player drops bomb by submitting row en column
        @app.route('/', methods=('GET', 'POST'))
        def create_html():

            # GET: display situation at start of game
            if request.method == 'GET':

                html = self._game_display() + self.__html_form()

            # POST: player drops bomb
            else:

                # input row and column
                row = int(request.form['row'])
                column = int(request.form['column'])
                
                # drop bomb and display
                self.drop_bomb(row, column)
                html = self._game_display()

                # game over -> shut down server
                if self.bombs_left == 0 or self.sunk:
                    request.environ.get('werkzeug.server.shutdown')()

                # game not over yet -> add form
                else:
                    html += self.__html_form()

            # return html string
            return html

        # run server app
        app.run()
