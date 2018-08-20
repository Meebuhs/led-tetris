import time
import sys
import threading
from random import shuffle
import Tetrominoes
import Display
import Constants
import Getch


# Maintain two global versions of the board, the first is an array of rows (starting at the top and moving down the
# board) which have one bit per column, each indicating whether the position is occupied. This does not include the
# falling tetromino
board = []
# The second is an array of RGB tuples storing the colour of each position. This does include the falling tetromino
board_display = []
# The game speed defines the number of milliseconds it takes for a block to fall one row
game_speed = 600
# The tetromino that is currently falling, as long as the game is running there will always be one. It is initialised
# to an I block but is overwritten as soon as the game starts and the queue is generated
falling_tetromino = Tetrominoes.I()
# The queue contains the order of tetrominoes to be dropped
queue = []
# Dimensions of the LED panels
Constants.BOARD_HEIGHT = 64
Constants.BOARD_WIDTH = 96
# Global game over signal to allow thread to signify game end
game_over = False

def generate_board():
    """ Initialises an empty board """
    global board
    board = [0] * Constants.BOARD_HEIGHT


def generate_display_board():
    """ Initialises an empty board display"""
    global board_display
    board_display = [(0, 0, 0)] * Constants.BOARD_WIDTH * Constants.BOARD_HEIGHT


def play_game():
    """ Main game loop which handles user input and the descent timing """
    global queue
    global game_over
    global falling_tetromino
    # Generate the queue of tetrominoes to be dropped
    queue = generate_queue()
    # Drop the tetromino at the front of the queue
    add_next_tetromino()

    # Records the time at which the tetromino was last dropped a row, setting it to the current time avoids
    # having it drop as soon as the game starts
    last_drop_time = time.time()

    # Start user input thread
    threading.Thread(target=input_thread).start()

    while True:
        # Check the game hasn't ended
        if game_over:
            break
        # Check if the tetromino needs to descend
        current_time = time.time()
        if (current_time - last_drop_time) * 1000 > game_speed:
            # Set the last drop time
            last_drop_time = current_time
            # Delay defined by game speed has passed, drop the tetromino
            if not attempt_drop_one_row(falling_tetromino):
                # Collision occurs, attach to board and attempt to drop next tetromino
                if not place_tetromino_and_create_next(falling_tetromino):
                    game_over = True
                    break


def input_thread():
    """ Checks user input and calls the appropriate functions. This method will run in its own thread so that it doesn't
    block the main game timer while waiting for input
    """
    global game_over
    lock = threading.Lock()
    while True:
        with lock:
            # Check game over
            if game_over:
                break
            user_input = Getch.getch()
            if user_input == 'w':
                # Rotate the tetromino
                attempt_rotation(falling_tetromino)
            elif user_input == 'a':
                # Move the tetromino left
                attempt_move("LEFT", falling_tetromino)
            elif user_input == 'd':
                # Move the tetromino right
                attempt_move("RIGHT", falling_tetromino)
            elif user_input == 's':
                # Soft drop the tetromino one row
                attempt_drop_one_row(falling_tetromino)
            elif user_input == ' ':
                # Hard drop the tetromino to the bottom of the board
                # Keep track of how many rows were skipped
                rows_dropped = 0
                # Keep dropping rows until a collision occurs
                while attempt_drop_one_row(falling_tetromino):
                    rows_dropped += 1
                # Tetromino collided, attach to board and attempt to drop the next tetromino
                if not place_tetromino_and_create_next(falling_tetromino):
                    game_over = True
                    break
            elif user_input == 'b':
                # Break the game process
                game_over = True
                break


def generate_queue():
    """ Generate the queue which defines the order in which tetrominoes are added to the board. The queue is a random
    permutation of the 7 ids (0..6) """
    global queue
    queue = list(range(7))
    shuffle(queue)
    return queue


def add_next_tetromino():
    """ Attempts to add the next tetromino in the queue. If the tetromino cannot be added then the
    game is over
    """
    global falling_tetromino
    falling_tetromino = get_tetromino_from_queue()
    # Check if the tetromino will collide
    if tetromino_collides(falling_tetromino):
        return False  # Game over

    add_tetromino_to_display(falling_tetromino)
    Display.update_display(board_display)

    # Successfully added
    return True


def get_tetromino_from_queue():
    """ Returns an instance of the tetromino at the front of the queue. If the queue is empty, a new queue is
    generated """
    global queue
    if not queue:
        queue = generate_queue()
    return get_tetromino(queue.pop(0))


def get_tetromino(tetromino_id):
    """ Returns the tetromino with the given id """
    return {
        0: Tetrominoes.I(),
        1: Tetrominoes.J(),
        2: Tetrominoes.L(),
        3: Tetrominoes.O(),
        4: Tetrominoes.S(),
        5: Tetrominoes.T(),
        6: Tetrominoes.Z()
    }.get(tetromino_id)


def tetromino_collides(tetromino):
    """ Checks if the tetromino will collide with an others on the board and returns True if a collision occurs """
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
    # Attempt to add the next tetromino
    return add_next_tetromino()


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
    print("you deaded loser")
    while True:
        user_input = sys.stdin.read(1)
        if user_input == 'r':
            break


if __name__ == "__main__":
    # Main game loop, is broken when a tetromino is blocked from entering the playing area
    while True:
        generate_board()
        generate_display_board()
        play_game()
        handle_game_end()
