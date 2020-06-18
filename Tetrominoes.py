import Constants
import time
from math import floor


class Tetromino(object):
    """ Base class from which all tetrominos inherit"""
    def __init__(self, game):
        # The number id of the game which the block was added to
        self.game = game
        # The x position of the block, starting in the middle of its respective game
        self.xpos = floor((Constants.BOARD_WIDTH / Constants.NUM_GAMES) * (game + 0.5))
        # The y position of the block, starting at the top
        self.ypos = 0
        # The rotation of the block, incrementing rotation by 1 symbolises a 90 degree rotation
        self.rotation = 0
        # The patterns for the block. A single pattern of a block is an array of binary numbers with a bit for each
        # column and a 1 indicating the position is occupied. The array contains as many numbers as the block has rows.
        self.patterns = []
        # Records the time at which the tetromino was last dropped a row, setting it to the current time avoids
        # having it drop as soon as the game starts
        self.last_drop_time = time.time()
        # The goal x position decided by the heuristic, initialised to -1 and changed when decided
        self.goal_xpos = -1
        # The goal rotation decided by the heuristic, initialised to -1 and changed when decided
        self.goal_rotation = -1


class I(Tetromino):
    """ I Block (1 x 4)
    ----  --*-  ----  -*--
    ****  --*-  ----  -*--
    ----  --*-  ****  -*--
    ----  --*-  ----  -*--
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b1111],
                         [0b1, 0b1, 0b1, 0b1]]
        self.xpos -= 2
        self.height = 1
        self.width = 4
        self.colour = (0, 120, 120)  # Cyan


class J(Tetromino):
    """ J Block (2 x 3)
    *--  -**  ---  -*-
    ***  --*  ***  -*-
    ---  --*  --*  **-
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b100, 0b111],
                         [0b11, 0b10, 0b10],
                         [0b111, 0b001],
                         [0b01, 0b01, 0b11]]
        self.xpos -= 1
        self.height = 2
        self.width = 3
        self.colour = (0, 0, 120)  # Blue


class L(Tetromino):
    """ L Block (2 x 3)
    --*  -*-  ---  **-
    ***  -*-  ***  -*-
    ---  -**  *--  -*-
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b001, 0b111],
                         [0b10, 0b10, 0b11],
                         [0b111, 0b100],
                         [0b11, 0b01, 0b01]]
        self.xpos -= 1
        self.height = 2
        self.width = 3
        self.colour = (120, 80, 0)  # Orange


class O(Tetromino):
    """ O Block (2 x 2)
    **
    **
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b11, 0b11]]
        self.height = 2
        self.width = 2
        self.colour = (120, 120, 0)  # Yellow


class S(Tetromino):
    """ S Block (2 x 3)
    -**  -*-  ---  *--
    **-  -**  -**  **-
    ---  --*  **-  -*-
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b011, 0b110],
                         [0b10, 0b11, 0b01]]
        self.xpos -= 1
        self.height = 2
        self.width = 3
        self.colour = (0, 120, 0)  # Green


class T(Tetromino):
    """ T Block (2 x 3)
    -*-  -*-  ---  -*-
    ***  -**  ***  **-
    ---  -*-  -*-  -*-
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b010, 0b111],
                         [0b10, 0b11, 0b10],
                         [0b111, 0b010],
                         [0b01, 0b11, 0b01]]
        self.xpos -= 1
        self.height = 2
        self.width = 3
        self.colour = (80, 0, 120)  # Purple


class Z(Tetromino):
    """ Z Block (2 x 3)
    **-  --*  ---  -*-
    -**  -**  **-  **-
    ---  -*-  -**  *--
    """
    def __init__(self, game):
        Tetromino.__init__(self, game)
        self.patterns = [[0b110, 0b011],
                         [0b01, 0b11, 0b10]]
        self.xpos -= 1
        self.height = 2
        self.width = 3
        self.colour = (120, 0, 0)  # Red
