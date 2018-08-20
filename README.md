# led-tetris
Tetris which runs on a raspberry pi and displays on a chain of led matrices using hzeller's rpi-rgb-led-matrix library.

![](https://i.imgur.com/TRBpEpu.jpg)

The game currently operates as you would expect from tetris, however using two chains of three 32x32 led matrices, the
board is simply too large for the game to be fun. The current plan is to transition this to a visualiser which uses a
heuristic to 'autoplay' tetris by dropping several pieces at a time.

## Requirements
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)

[Pillow](https://github.com/python-pillow/Pillow)
