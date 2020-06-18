from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import Constants

options = RGBMatrixOptions()
#options.rows = Constants.BOARD_HEIGHT
#options.cols = Constants.BOARD_WIDTH
options.chain_length = Constants.CHAIN_LENGTH
options.parallel = Constants.PARALLEL_CHAINS
options.hardware_mapping = 'regular'
#options.no_hardware_pulse = 1

matrix = RGBMatrix(options=options)
offscreen_canvas = matrix.CreateFrameCanvas()


def update_display(board_display):
    """ Takes the board display which is a list of RGB tuples and sets the display of the panels """
    global offscreen_canvas
    global matrix
    image = Image.new("RGB", (Constants.BOARD_WIDTH, Constants.BOARD_HEIGHT))
    image.putdata(board_display)
    offscreen_canvas.SetImage(image.convert('RGB'))
    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
