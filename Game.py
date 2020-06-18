import time
import sys
from random import randint
import Tetrominoes
import Display
import Constants


# Maintain three global versions of the board. The first contains only the tetrominoes which have been placed on the
# board via a collision. It is an arrays of binary numbers, each representing a row starting at the top of the board,
# where each bit indicates whether the position is occupied.
board = []
# This contains the placed tetrominoes as well as the final position of any falling tetrominoes once they have been
# decided and is structured the same as board.
decided_board = []
# The third is an array of RGB tuples storing the colour of each position. This does include any falling tetrominoes.
board_display = []
# The game speed defines the number of milliseconds it takes for a block to fall one row
game_speed = Constants.GAME_SPEED
# A list of length NUM_GAMES, where each item is a list of tetrominoes falling within a given game. Tetrominoes remain
# in their respective list until they collide with a piece or the bottom of the game
falling_tetrominoes = [[] for game in range(Constants.NUM_GAMES)]
# Global game over signal to allow thread to signify game end
game_over = False


def initialise_game():
    """ Initialises the data structures used to keep track of the game """
    initialise_board()
    initialise_decided_board()
    initialise_display_board()
    initialise_falling_tetrominoes()


def initialise_board():
    """ Initialises an empty board """
    global board
    board = [0] * Constants.BOARD_HEIGHT


def initialise_decided_board():
    """ Initialises an empty decided board """
    global decided_board
    decided_board = [0] * Constants.BOARD_HEIGHT


def initialise_display_board():
    """ Initialises an empty board display """
    global board_display
    board_display = [(0, 0, 0)] * Constants.BOARD_WIDTH * Constants.BOARD_HEIGHT


def initialise_falling_tetrominoes():
    """ Initialises the falling tetrominoes """
    global falling_tetrominoes
    falling_tetrominoes = [[] for game in range(Constants.NUM_GAMES)]


def play_game():
    """ Main game loop which handles the descent timing """
    global game_over
    global falling_tetrominoes

    drop_count = 0
    expected_drops = (Constants.BOARD_HEIGHT - Constants.DROP_SPACING) / Constants.DROP_SPACING * Constants.NUM_GAMES
    last_dropped_time = time.time()

    while True:
        # Drop tetrominoes at the start of the game
        if drop_count < expected_drops:
            if handle_dropping_tetrominoes(drop_count, last_dropped_time):
                drop_count += 1
                last_dropped_time = time.time()

        # Check the game hasn't ended
        if game_over:
            break
        # Check if the tetromino needs to descend
        current_time = time.time()
        for game in range(Constants.NUM_GAMES):
            for tetromino in falling_tetrominoes[game]:
                if (current_time - tetromino.last_drop_time) * 1000 > game_speed:
                    # Set the last drop time
                    tetromino.last_drop_time = current_time
                    # Delay defined by game speed has passed, drop the tetromino
                    if not attempt_drop_one_row(tetromino):
                        # Collision occurs, attach to board and attempt to drop next tetromino
                        if not place_tetromino_and_create_next(tetromino):
                            game_over = True
                            break


def handle_dropping_tetrominoes(drop_count, last_dropped_time):
    """ Drops the initials tetrominoes evenly across the width of the board. Returns True if a tetromino is dropped. """
    # Space the tetromino drops evenly to maintain DROP_SPACING across NUM_GAMES games
    if time.time() - last_dropped_time >= Constants.DROP_SPACING / Constants.NUM_GAMES * Constants.GAME_SPEED:
        add_next_tetromino(drop_count)
        return True
    return False


def add_next_tetromino(game):
    """ Attempts to add a new tetromino for a game. If the tetromino cannot be added then the game is over """
    global falling_tetrominoes
    new_tetromino = get_tetromino(game)
    falling_tetrominoes[game].append(new_tetromino)
    # Check if the tetromino will collide
    if tetromino_collides(new_tetromino):
        return False  # Game over

    add_tetromino_to_display(new_tetromino)
    Display.update_display(board_display)

    # Successfully added
    return True


def get_tetromino(game):
    """ Returns the tetromino with the given id """
    return {
        0: Tetrominoes.I(game),
        1: Tetrominoes.J(game),
        2: Tetrominoes.L(game),
        3: Tetrominoes.O(game),
        4: Tetrominoes.S(game),
        5: Tetrominoes.T(game),
        6: Tetrominoes.Z(game)
    }.get(randint(0, 6))


def tetromino_collides(tetromino):
    """ Checks if the tetromino will collide with any others on the board and returns True if a collision occurs """
    for row in range(tetromino.height):
        # Only check if row is non-zero, i.e. the tetromino occupies space in the row
        if tetromino.patterns[tetromino.rotation][row]:
            # Bitwise AND the tetromino pattern in position with the board, collision occurs if result > 0
            tetromino_bit_pattern = tetromino.patterns[tetromino.rotation][row] << tetromino.xpos
            if tetromino_bit_pattern & board[tetromino.ypos + row]:
                return True
    # No collisions
    return False


def attempt_rotation(tetromino):
    """ Checks if the tetromino can be rotated and does so if possible """
    # After rotation, the height and width of the block will have swapped, check it still fits in the play area
    if tetromino.xpos + tetromino.height > Constants.BOARD_WIDTH:
        # Tetromino extends past right edge of board
        return False
    if tetromino.ypos + tetromino.width > Constants.BOARD_HEIGHT:
        # Tetromino extends past bottom of board
        return False

    # The tetromino would remain in the play area, check for collisions
    tetromino.rotation = (tetromino.rotation + 1) % len(tetromino.patterns)
    new_width = tetromino.height
    tetromino.height = tetromino.width
    tetromino.width = new_width
    if tetromino_collides(tetromino):
        # The tetromino collides, move not possible
        tetromino.rotation = (tetromino.rotation - 1) % len(tetromino.patterns)
        new_width = tetromino.height
        tetromino.height = tetromino.width
        tetromino.width = new_width
        return False

    new_width = tetromino.height
    tetromino.height = tetromino.width
    tetromino.width = new_width
    tetromino.rotation = (tetromino.rotation - 1) % len(tetromino.patterns)
    remove_tetromino_from_display(tetromino)

    # Perform the rotation by incrementing the value and wrapping back if we extend past the number of patterns
    tetromino.rotation = (tetromino.rotation + 1) % len(tetromino.patterns)
    new_width = tetromino.height
    tetromino.height = tetromino.width
    tetromino.width = new_width

    add_tetromino_to_display(tetromino)

    Display.update_display(board_display)
    return True


def attempt_move(direction, tetromino):
    """ Attempt to move the tetromino in the specified direction. This will fail if it pushes the tetromino out of the
     playable area or if it will collide with another tetromino """
    if direction == "LEFT":
        attempt_move_left(tetromino)
    elif direction == "RIGHT":
        attempt_move_right(tetromino)


def attempt_move_left(tetromino):
    """ Checks if the tetromino can be moved left and does so if possible """
    if tetromino.xpos - 1 < 0:
        # The tetromino would leave left edge
        return False

    # The tetromino would remain in the play area, check for collisions
    tetromino.xpos -= 1
    if tetromino_collides(tetromino):
        # The tetromino collides, move not possible
        tetromino.xpos += 1
        return False

    # The move is possible, make it
    tetromino.xpos += 1
    remove_tetromino_from_display(tetromino)
    tetromino.xpos -= 1
    add_tetromino_to_display(tetromino)

    Display.update_display(board_display)
    return True


def attempt_move_right(tetromino):
    """ Checks if the tetromino can be moved right and does so if possible """
    # Position is top left corner of tetromino
    if tetromino.xpos + tetromino.width + 1 > Constants.BOARD_WIDTH:
        # The tetromino would leave right edge
        return False

    # The tetromino would remain in the play area, check for collisions
    tetromino.xpos += 1
    if tetromino_collides(tetromino):
        # The tetromino collides, move not possible
        tetromino.xpos -= 1
        return False

    # The move is possible, make it
    tetromino.xpos -= 1
    remove_tetromino_from_display(tetromino)
    tetromino.xpos += 1
    add_tetromino_to_display(tetromino)

    Display.update_display(board_display)
    return True


def attempt_drop_one_row(tetromino):
    """ Checks if the tetromino can move down a row and does so if possible.
    Returns false if it extends off the top of the playing area
    """
    # If the tetromino has reached the bottom of the board the move fails
    if tetromino.ypos + tetromino.height >= Constants.BOARD_HEIGHT:
        return False

    # The tetromino would remain in the play area, check for collisions
    tetromino.ypos += 1
    if tetromino_collides(tetromino):
        # The tetromino collides, move not possible
        tetromino.ypos -= 1
        return False

    # The move is possible, make it
    tetromino.ypos -= 1
    remove_tetromino_from_display(tetromino)
    tetromino.ypos += 1
    add_tetromino_to_display(tetromino)

    Display.update_display(board_display)
    return True


def place_tetromino_and_create_next(tetromino):
    """ Adds tetromino to the board at its current position. This is done by performing a bitwise or on each row
    the tetromino is in. We then attempt to add a new tetromino at the top of the board. Returns true if this is
    successful and false if not (signifying the game is over) """
    global board
    # Add the tetromino to the board representation
    for row in range(tetromino.height):
        if tetromino.patterns[tetromino.rotation][row]:
            board_row = tetromino.ypos + row
            # OR the tetromino in position with the row
            board[board_row] |= (tetromino.patterns[tetromino.rotation][row] << tetromino.xpos)
    # Check if it completed any rows
    check_for_completed_rows(tetromino)
    # Remove the tetromino from the falling tetrominoes
    falling_tetrominoes[tetromino.game].remove(tetromino)
    # Attempt to add the next tetromino
    return add_next_tetromino(tetromino.game)


def check_for_completed_rows(tetromino):
    """ Checks for any completed rows and removes them. Higher rows are shifted down to fill removed rows and empty rows
    are added at the top of the board. The display is updated if any changes are made
    """
    global board
    global board_display
    lines_cleared = False
    for row in range(tetromino.height):
        board_row = tetromino.ypos + row
        if board[board_row] == ((1 << Constants.BOARD_WIDTH) - 1):
            # Line is complete, clear it
            lines_cleared = True
            increment_game_speed()
            # Copy every row above the current row down one space in both board and board_display
            for i in range(board_row + 1):
                board[board_row - i] = board[board_row - i - 1]
                for j in range(Constants.BOARD_WIDTH):
                    board_display[(board_row - i) * Constants.BOARD_WIDTH + j] = board_display[
                        (board_row - i - 1) * Constants.BOARD_WIDTH + j]
            # Add an empty row at the top
            board[0] = 0
            for column in range(Constants.BOARD_WIDTH):
                board_display[column] = (0, 0, 0)
    if lines_cleared:
        Display.update_display(board_display)


def increment_game_speed():
    """ Lowers the time between each drop """
    global game_speed
    if game_speed > 150:
        game_speed -= 15


def add_tetromino_to_display(tetromino):
    """ Adds the entries for tetromino to the board display """
    global board_display
    for row in range(tetromino.height):
        board_row = tetromino.ypos + row
        for column in range(tetromino.width):
            if tetromino.patterns[tetromino.rotation][row] & (1 << column):
                # This position in the tetromino is occupied, add to display
                board_column = tetromino.xpos + column
                board_display[board_row * Constants.BOARD_WIDTH + board_column] = tetromino.colour


def remove_tetromino_from_display(tetromino):
    """ Removes the entries for tetromino from the board display """
    global board_display
    for row in range(len(tetromino.patterns[tetromino.rotation])):
        board_row = tetromino.ypos + row
        for column in range(tetromino.width):
            if tetromino.patterns[tetromino.rotation][row] & (1 << column):
                # This position in the tetromino is occupied, remove from display
                board_column = tetromino.xpos + column
                board_display[board_row * Constants.BOARD_WIDTH + board_column] = (0, 0, 0)


def handle_game_end():
    print("Game ended")
    print("Type 'n' to start a new game")
    while True:
        user_input = sys.stdin.read(1)
        if user_input == 'n':
            reset_game_properties()
            break


def reset_game_properties():
    global game_over
    game_over = False
    global game_speed
    game_speed = Constants.GAME_SPEED


if __name__ == "__main__":
    # Main game loop, is broken when a tetromino is blocked from entering the playing area
    while True:
        initialise_game()
        play_game()
        handle_game_end()
