# LED tetris

An AI which uses a heuristic to autoplay tetris with multiple concurrently falling tetrominoes on an array of led 
matrices. 

The tetris game code features a lot of bit bashing as it was originally a uni project written in C to run on an 
ATmega324A microcontroller.

![](docs/led-tetris-demo.gif)

## Getting started
### Physical setup

The project runs on a raspberry pi and is displayed on six 32x32 P6 SMD3528 LED matrices. These matrices must be 
connected to the raspberry pi as outlined in the 
[rpi-rgb-led-matrix wiring documentation](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/wiring/md) along 
with a sufficient power supply. 

### Software setup

First install the project requirements.

```shell
sudo apt-get update && sudo apt-get install python3-dev python3-pillow -y
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
```

These instructions are correct as of 20 June 2020. Up to date installation instructions may be found in the 
documentation of the [requirements](#requirements).

Then download and run the script.

```shell
git clone https://github.com/Meebuhs/led-tetris.git
cd led-tetris
sudo python3 Game.py 
```

## Configuration

There are some editable settings in Constant.py.

| Property        | Description                                                       |
|-----------------|-------------------------------------------------------------------|
| CHAIN_LENGTH    | The length of the led matrix chains                               |
| PARALLEL_CHAINS | The number of led matrix chains                                   |
| BOARD_WIDTH     | The pixel width of a single matrix                                |
| BOARD_HEIGHT    | The pixel height of a single matrix                               |
| NUM_GAMES       | The number of tetrominoes that drop at one time                   |
| GAME_SPEED      | The time it takes for a tetromino to drop one line (milliseconds) | 
| FACTORS         | The scores assigned by the heuristic for a given condition        |


## Requirements
[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix)

[Pillow](https://github.com/python-pillow/Pillow)